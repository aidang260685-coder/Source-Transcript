#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcribe_batch.py - Phiên âm hàng loạt file ghi âm họp (m4a/wma/mp3/wav/mp4...) sang tiếng Việt.

Quy trình mỗi file:
  1. ffmpeg: chuyển sang WAV mono 16 kHz (kèm lọc low-cut, chuẩn hoá âm lượng, tùy chọn khử ồn)
  2. faster-whisper (Whisper large-v3, ép ngôn ngữ 'vi', VAD bỏ đoạn im lặng)
  3. Lọc ảo giác (hallucination) tiếng Việt phổ biến của Whisper ở đoạn ồn/im lặng
  4. Áp glossary: sửa lỗi nhận dạng thuật ngữ/tên riêng + chuẩn hoá dấu tiếng Việt (NFC, kiểu dấu mới/cũ)
  5. Xuất: <tên>.txt (có mốc thời gian), <tên>.srt, <tên>_flagged.txt (danh sách đoạn [??]),
     và 1 file gộp ALL_transcripts.txt

Cài đặt:
    pip install faster-whisper
    # và cài ffmpeg (https://ffmpeg.org) sao cho lệnh `ffmpeg` chạy được trong terminal

Dùng:
    python transcribe_batch.py ./ghi_am ./transcripts
    python transcribe_batch.py ./ghi_am ./transcripts --glossary glossary.txt --denoise
    python transcribe_batch.py ./ghi_am ./transcripts --model medium      # máy yếu, không có GPU
"""

import argparse
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

# Đảm bảo console Windows hiển thị đúng tiếng Việt UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

AUDIO_EXT = {".m4a", ".wma", ".mp3", ".wav", ".aac", ".ogg", ".flac", ".mp4", ".mkv", ".mov"}

# Các câu ảo giác (hallucination) kinh điển của Whisper tiếng Việt khi gặp đoạn im lặng/nhiễu nền
HALLUCINATION_PATTERNS = [
    re.compile(r"^hãy\s+subscribe\s+cho\s+kênh", re.IGNORECASE),
    re.compile(r"để\s+không\s+bỏ\s+lỡ\s+những\s+video\s+hấp\s+dẫn", re.IGNORECASE),
    re.compile(r"^cảm\s+ơn\s+(các\s+bạn|quý\s+vị)\s+đã\s+(xem|theo\s+dõi|lắng\s+nghe)", re.IGNORECASE),
    re.compile(r"^hẹn\s+gặp\s+lại\s+(các\s+bạn|quý\s+vị)\s+trong\s+những\s+video\s+tiếp\s+theo", re.IGNORECASE),
    re.compile(r"^subtitles?\s+by", re.IGNORECASE),
    re.compile(r"^amara\.org", re.IGNORECASE),
    re.compile(r"^ghi\s+ền\s+mì\s+gõ", re.IGNORECASE),
    re.compile(r"^la\s+la\s+school", re.IGNORECASE),
]

# Ranh giới từ tương thích tiếng Việt & ký tự đặc biệt (thay cho \w vốn lỗi với từ chứa dấu gạch/chấm)
WORD_BOUNDARY_LEFT = r"(?<![0-9A-Za-zÀ-ỹ_])"
WORD_BOUNDARY_RIGHT = r"(?![0-9A-Za-zÀ-ỹ_])"


# ----------------------------------------------------------------------------- glossary & text cleanup
def normalize_vn(text: str) -> str:
    """Chuẩn hoá Unicode dựng sẵn (NFC) và khoảng trắng thừa quanh dấu câu."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:?!])", r"\1", text)
    return text


def is_hallucination(text: str) -> bool:
    """Kiểm tra xem câu nhận dạng có phải ảo giác đặc trưng của Whisper trên tiếng Việt không."""
    clean = normalize_vn(text)
    if not clean:
        return True
    for pat in HALLUCINATION_PATTERNS:
        if pat.search(clean):
            return True
    # Lặp một cụm ngắn >= 4 lần liên tiếp (ảo giác lặp)
    words = clean.lower().split()
    if len(words) >= 8 and len(set(words)) <= 2:
        return True
    return False


def load_glossary(path: Path | None):
    """Đọc glossary.txt.
    - Dòng 'sai => đúng'  : thay thế sau khi phiên âm (không phân biệt hoa/thường, ưu tiên cụm dài trước).
    - Dòng chỉ có 1 thuật ngữ: đưa vào initial_prompt để model ưu tiên nhận đúng.
    - Dòng bắt đầu bằng '#': ghi chú.
    """
    terms, raw_fixes = [], []
    if not path or not path.exists():
        return terms, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = normalize_vn(raw)
        if not line or line.startswith("#"):
            continue
        if "=>" in line:
            wrong, right = (s.strip() for s in line.split("=>", 1))
            if wrong and right:
                raw_fixes.append((wrong, right))
                terms.append(right)
        else:
            terms.append(line)

    # Sắp xếp cụm dài trước để không bị cụm ngắn cắt ngang
    raw_fixes.sort(key=lambda pair: len(pair[0]), reverse=True)
    fixes = [
        (
            re.compile(WORD_BOUNDARY_LEFT + re.escape(wrong) + WORD_BOUNDARY_RIGHT, re.IGNORECASE),
            right,
        )
        for wrong, right in raw_fixes
    ]

    # Loại trùng thuật ngữ, giữ thứ tự
    seen, uniq = set(), []
    for t in terms:
        if t.lower() not in seen:
            seen.add(t.lower())
            uniq.append(t)
    return uniq, fixes


def build_prompt(terms: list[str]) -> str:
    """Tạo initial_prompt cho Whisper (giới hạn độ dài an toàn < 224 tokens, không cắt ngang từ)."""
    base = (
        "Biên bản cuộc họp công việc bằng tiếng Việt chuẩn chính tả, "
        "xưng hô Anh, Chị, Em, viết hoa tên riêng và thuật ngữ."
    )
    if not terms:
        return base
    selected = []
    current_len = 0
    for term in terms:
        if current_len + len(term) + 2 > 420:
            break
        selected.append(term)
        current_len += len(term) + 2
    return f"{base} Thuật ngữ và tên riêng: {', '.join(selected)}."


def apply_fixes(text: str, fixes) -> str:
    text = normalize_vn(text)
    for pattern, right in fixes:
        text = pattern.sub(right, text)
    return normalize_vn(text)


# ----------------------------------------------------------------------------- audio
def to_wav(src: Path, dst: Path, denoise: bool, loudnorm: bool = True):
    filters = ["highpass=f=80", "lowpass=f=7600"]
    if denoise:
        filters.append("afftdn=nf=-25")
    if loudnorm:
        filters.append("dynaudnorm=f=150:g=15")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
        "-vn", "-ac", "1", "-ar", "16000", "-af", ",".join(filters), str(dst),
    ]
    subprocess.run(cmd, check=True)


def detect_device(requested: str):
    if requested != "auto":
        return requested, ("float16" if requested == "cuda" else "int8")
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


# ----------------------------------------------------------------------------- format
def ts(seconds: float, srt: bool = False) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}" if srt else f"{h:02d}:{m:02d}:{s:02d}"


def write_outputs(out_dir: Path, rel_stem: str, rows):
    txt_file = out_dir / f"{rel_stem}.txt"
    srt_file = out_dir / f"{rel_stem}.srt"
    flag_file = out_dir / f"{rel_stem}_flagged.txt"

    txt_file.parent.mkdir(parents=True, exist_ok=True)

    flagged_rows = []
    with txt_file.open("w", encoding="utf-8") as f:
        for start, end, text in rows:
            f.write(f"[{ts(start)}] {text}\n")
            if "[??]" in text:
                flagged_rows.append((start, end, text))

    with srt_file.open("w", encoding="utf-8") as f:
        for i, (start, end, text) in enumerate(rows, 1):
            f.write(f"{i}\n{ts(start, True)} --> {ts(end, True)}\n{text}\n\n")

    if flagged_rows:
        with flag_file.open("w", encoding="utf-8") as f:
            f.write(f"# DANH SÁCH ĐOẠN CẦN NGHE KIỂM TRA LẠI ({len(flagged_rows)} đoạn)\n")
            for start, end, text in flagged_rows:
                f.write(f"[{ts(start)} -> {ts(end)}] {text}\n")


def make_rel_stem(input_dir: Path, src: Path) -> str:
    """Tạo tên file đầu ra duy nhất kể cả khi có thư mục con trùng tên file."""
    try:
        rel = src.relative_to(input_dir).with_suffix("")
        return "__".join(rel.parts)
    except ValueError:
        return src.stem


# ----------------------------------------------------------------------------- main
def main():
    script_dir = Path(__file__).resolve().parent
    default_glossary = script_dir / "glossary.txt"
    if not default_glossary.exists():
        default_glossary = Path("glossary.txt")

    ap = argparse.ArgumentParser(description="Phiên âm hàng loạt tiếng Việt bằng faster-whisper")
    ap.add_argument("input_dir", type=Path, help="Thư mục chứa file ghi âm (.m4a, .mp3, .wav...)")
    ap.add_argument("output_dir", type=Path, help="Thư mục xuất transcript")
    ap.add_argument("--glossary", type=Path, default=default_glossary, help="Đường dẫn file glossary.txt")
    ap.add_argument("--model", default="large-v3", help="large-v3 (chính xác nhất) | medium | small")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--denoise", action="store_true", help="Khử ồn nhẹ bằng ffmpeg afftdn")
    ap.add_argument("--no-loudnorm", action="store_true", help="Tắt cân bằng âm lượng tự động")
    ap.add_argument("--flag-threshold", type=float, default=-0.85,
                    help="avg_logprob thấp hơn mức này sẽ gắn [??] (mặc định -0.85)")
    ap.add_argument("--overwrite", action="store_true", help="Phiên âm lại cả file đã có kết quả")
    args = ap.parse_args()

    if not args.input_dir.exists():
        sys.exit(f"Thư mục đầu vào không tồn tại: {args.input_dir}")

    files = sorted(p for p in args.input_dir.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXT)
    if not files:
        sys.exit(f"Không tìm thấy file âm thanh ({', '.join(sorted(AUDIO_EXT))}) trong {args.input_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("Thiếu thư viện. Chạy: pip install faster-whisper")

    device, ctype = detect_device(args.device)
    terms, fixes = load_glossary(args.glossary)
    prompt = build_prompt(terms)

    print(f"Model={args.model} | device={device} ({ctype}) | số file={len(files)}")
    print(f"Glossary: {len(terms)} thuật ngữ, {len(fixes)} quy tắc sửa lỗi ({args.glossary})")
    model = WhisperModel(args.model, device=device, compute_type=ctype)

    combined = []

    for idx, src in enumerate(files, 1):
        rel_stem = make_rel_stem(args.input_dir, src)
        txt_path = args.output_dir / f"{rel_stem}.txt"
        print(f"\n[{idx}/{len(files)}] {src.name} -> {rel_stem}.txt")

        if txt_path.exists() and not args.overwrite:
            print("  - Đã có transcript, bỏ qua (dùng --overwrite để làm lại)")
            combined.append((rel_stem, txt_path.read_text(encoding="utf-8")))
            continue

        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "audio.wav"
            try:
                to_wav(src, wav, denoise=args.denoise, loudnorm=not args.no_loudnorm)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"  ! Lỗi ffmpeg ({e}). Kiểm tra ffmpeg đã cài chưa. Bỏ qua file này.")
                continue

            segments, info = model.transcribe(
                str(wav),
                language="vi",
                beam_size=5,
                best_of=5,
                temperature=(0.0, 0.2, 0.4),
                compression_ratio_threshold=2.2,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=450, speech_pad_ms=250),
                condition_on_previous_text=False,  # tránh lặp câu/ảo giác kéo dài
                initial_prompt=prompt,
            )

            rows, flagged, skipped_hallucination = [], 0, 0
            total_dur = max(info.duration, 0.1)
            for seg in segments:
                text = seg.text.strip()
                if not text:
                    continue
                if seg.no_speech_prob > 0.75 and seg.avg_logprob < -0.9:
                    continue
                if is_hallucination(text):
                    skipped_hallucination += 1
                    continue

                text = apply_fixes(text, fixes)
                # Gắn cờ [??] khi độ tự tin thấp hoặc độ nén bất thường
                if seg.avg_logprob < args.flag_threshold or seg.compression_ratio > 2.0:
                    text += " [??]"
                    flagged += 1

                rows.append((seg.start, seg.end, text))
                print(f"\r  - Tiến độ: {ts(seg.end)} / {ts(total_dur)}", end="", flush=True)

        write_outputs(args.output_dir, rel_stem, rows)
        print(
            f"\n  ✓ Hoàn tất: {len(rows)} đoạn | "
            f"{flagged} đoạn gắn [??] | "
            f"đã lọc {skipped_hallucination} đoạn nhiễu/ảo giác"
        )
        combined.append((rel_stem, txt_path.read_text(encoding="utf-8")))

    # Gộp tất cả vào 1 file để tạo biên bản họp
    all_path = args.output_dir / "ALL_transcripts.txt"
    with all_path.open("w", encoding="utf-8") as f:
        for stem, body in combined:
            f.write(f"===== {stem} =====\n{body}\n")
    print(f"\n✓ Xong toàn bộ. Kết quả tại: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
