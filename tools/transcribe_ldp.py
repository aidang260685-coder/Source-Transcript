# -*- coding: utf-8 -*-
"""
transcribe_ldp.py - Phiên âm cuộc họp chương trình học LDP (Leader Development Program)
Tập tin âm thanh: doc/ghi_am/11-07-2026 09.08_1.m4a
Đầu ra: doc/transcripts/11-07-2026 09.08_1_LDP.txt (.srt)
"""
import os
import sys
import time
import unicodedata
import re
from pathlib import Path

# Đảm bảo UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent

# Cấu hình DLL cho CUDA cublas
cublas_dir = BASE_DIR / ".venv" / "Lib" / "site-packages" / "nvidia" / "cublas" / "bin"
if cublas_dir.exists():
    os.add_dll_directory(str(cublas_dir))
    os.environ["PATH"] = str(cublas_dir) + os.pathsep + os.environ.get("PATH", "")

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

WORD_BOUNDARY_LEFT = r"(?<![0-9A-Za-zÀ-ỹ_])"
WORD_BOUNDARY_RIGHT = r"(?![0-9A-Za-zÀ-ỹ_])"

def normalize_vn(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:?!])", r"\1", text)
    return text

def is_hallucination(text: str) -> bool:
    clean = normalize_vn(text)
    if not clean:
        return True
    for pat in HALLUCINATION_PATTERNS:
        if pat.search(clean):
            return True
    words = clean.lower().split()
    if len(words) >= 8 and len(set(words)) <= 2:
        return True
    return False

def load_glossary(path: Path):
    terms, raw_fixes = [], []
    if path.exists():
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

    raw_fixes.sort(key=lambda pair: len(pair[0]), reverse=True)
    fixes = [
        (
            re.compile(WORD_BOUNDARY_LEFT + re.escape(wrong) + WORD_BOUNDARY_RIGHT, re.IGNORECASE),
            right,
        )
        for wrong, right in raw_fixes
    ]
    return terms, fixes

def apply_fixes(text: str, fixes) -> str:
    text = normalize_vn(text)
    for pattern, right in fixes:
        text = pattern.sub(right, text)
    return normalize_vn(text)

def ts(seconds: float, srt: bool = False) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}" if srt else f"{h:02d}:{m:02d}:{s:02d}"

def main():
    audio_path = BASE_DIR / "doc" / "ghi_am" / "11-07-2026 09.08_1.m4a"
    out_dir = BASE_DIR / "doc" / "transcripts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_txt = out_dir / "11-07-2026 09.08_1_LDP.txt"
    out_srt = out_dir / "11-07-2026 09.08_1_LDP.srt"
    glossary_path = BASE_DIR / "doc" / "glossary.txt"

    if not audio_path.exists():
        sys.exit(f"Không tìm thấy file: {audio_path}")

    terms, fixes = load_glossary(glossary_path)

    initial_prompt = (
        "Biên bản cuộc họp chương trình học LDP Leader Development Program Công ty Kiên Thành Tín KTT. "
        "Thành phần tham dự: Thầy Minh, Chị Thanh BOD CEO, Anh Thanh Duy MKT Marketing, "
        "Chị Hoài Thu KT Kế toán, Anh Quang Tuẩn Kinh doanh Sale, Chị Thúy Ngọc HR Nhân sự, "
        "Anh Hoàng Ân IT, Chị Linh Nhi Mua hàng Planning PP. "
        "Nội dung: Đào tạo lãnh đạo, phát triển năng lực quản lý, kế hoạch triển khai, bài tập thực hành, KPIs và đánh giá."
    )

    from faster_whisper import WhisperModel
    model_dir = BASE_DIR / "models" / "faster-whisper-small"
    print("Khởi tạo WhisperModel (small, cuda, float16)...", flush=True)
    model = WhisperModel(str(model_dir), device="cuda", compute_type="float16", local_files_only=True)

    print(f"Bắt đầu phiên âm tệp: {audio_path.name}", flush=True)
    start_time = time.time()

    segments, info = model.transcribe(
        str(audio_path),
        language="vi",
        beam_size=3,
        best_of=3,
        temperature=0.0,
        compression_ratio_threshold=2.2,
        log_prob_threshold=-1.0,
        no_speech_threshold=0.6,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=250),
        condition_on_previous_text=False,
        initial_prompt=initial_prompt,
    )

    total_dur = max(info.duration, 0.1)
    print(f"Tổng thời lượng âm thanh: {ts(total_dur)} ({total_dur:.1f} giây)", flush=True)

    txt_f = open(out_txt, "w", encoding="utf-8")
    srt_f = open(out_srt, "w", encoding="utf-8")

    txt_f.write(f"===== 11-07-2026 09.08_1.m4a (00:00 -> {ts(total_dur)}) =====\n")
    txt_f.flush()

    count = 0
    flagged = 0
    skipped = 0

    try:
        for seg in segments:
            text = seg.text.strip()
            if not text:
                continue
            if seg.no_speech_prob > 0.75 and seg.avg_logprob < -0.9:
                continue
            if is_hallucination(text):
                skipped += 1
                continue

            text = apply_fixes(text, fixes)
            if seg.avg_logprob < -0.85 or seg.compression_ratio > 2.0:
                text += " [??]"
                flagged += 1

            count += 1
            txt_f.write(f"[{ts(seg.start)}] {text}\n")
            txt_f.flush()

            srt_f.write(f"{count}\n{ts(seg.start, True)} --> {ts(seg.end, True)}\n{text}\n\n")
            srt_f.flush()

            if count % 10 == 0:
                elapsed = time.time() - start_time
                speed = seg.end / max(elapsed, 0.001)
                percent = (seg.end / total_dur) * 100
                print(f"[{ts(seg.end)} / {ts(total_dur)}] ({percent:.1f}%) | {speed:.1f}x | {text[:50]}...", flush=True)

    finally:
        txt_f.close()
        srt_f.close()

    elapsed = time.time() - start_time
    print(f"\n✓ Hoàn tất phiên âm trong {elapsed:.1f}s ({elapsed/60:.1f} phút)!", flush=True)
    print(f"✓ Tổng số phân đoạn: {count} | Gắn cờ [??]: {flagged} | Lọc bỏ: {skipped}", flush=True)
    print(f"✓ File kết quả: {out_txt}", flush=True)

if __name__ == "__main__":
    main()
