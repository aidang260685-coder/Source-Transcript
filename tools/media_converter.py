# -*- coding: utf-8 -*-
"""
media_converter.py - Chuyển đổi video/audio đa định dạng sang MP3 và WAV chuẩn AI.
Tuân thủ chính sách Zero Hardcoding và bảo mật thực thi an toàn (shell=False).
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent

COMMON_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".wma", ".aiff"}
COMMON_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv", ".flv"}

def get_ffmpeg_binary() -> str:
    """
    Xác định đường dẫn nhị phân của FFmpeg.
    Ưu tiên:
      1. Biến môi trường FFMPEG_PATH
      2. FFmpeg trong PATH hệ thống
      3. File ffmpeg.exe trong thư mục tools/ hoặc bin/ của dự án
    """
    env_path = os.environ.get("FFMPEG_PATH")
    if env_path and Path(env_path).is_file():
        return env_path

    system_which = shutil.which("ffmpeg")
    if system_which:
        return system_which

    local_candidates = [
        BASE_DIR / "bin" / "ffmpeg.exe",
        BASE_DIR / "tools" / "ffmpeg.exe",
        BASE_DIR / "ffmpeg.exe",
    ]
    prog_x86 = os.environ.get("ProgramFiles(x86)")
    if prog_x86:
        local_candidates.append(Path(prog_x86) / "ClipGrab" / "ffmpeg.exe")
    prog_normal = os.environ.get("ProgramFiles")
    if prog_normal:
        local_candidates.append(Path(prog_normal) / "ClipGrab" / "ffmpeg.exe")
    for candidate in local_candidates:
        if candidate.is_file():
            return str(candidate)

    return "ffmpeg"


def is_ffmpeg_available() -> bool:
    """Kiểm tra FFmpeg có sẵn sàng thực thi không."""
    cmd = get_ffmpeg_binary()
    try:
        proc = subprocess.run([cmd, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return proc.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def convert_to_mp3(
    input_path: Path,
    output_path: Optional[Path] = None,
    bitrate: str = "320k",
    sample_rate: int = 44100,
    channels: int = 2
) -> Path:
    """
    Chuyển đổi video (MP4, MKV,...) hoặc audio (FLAC, M4A,...) sang MP3 chất lượng cao.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file đầu vào: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".mp3")
    else:
        output_path = Path(output_path).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "libmp3lame",
        "-b:a", str(bitrate),
        "-ar", str(sample_rate),
        "-ac", str(channels),
        str(output_path)
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg chuyển đổi sang MP3 thất bại: {proc.stderr}")
    except FileNotFoundError as err:
        raise RuntimeError(
            "Không tìm thấy FFmpeg trên hệ thống. Hãy cài đặt FFmpeg hoặc đặt file ffmpeg.exe vào thư mục 'tools/'."
        ) from err

    return output_path


def extract_clean_wav_for_ai(
    input_path: Path,
    output_path: Optional[Path] = None,
    sample_rate: int = 16000
) -> Path:
    """
    Trích xuất âm thanh sang định dạng WAV Mono 16kHz kèm bộ lọc tối ưu cho mô hình Whisper/Demucs.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file đầu vào: {input_path}")

    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_ai_16k.wav")
    else:
        output_path = Path(output_path).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = get_ffmpeg_binary()
    # Bộ lọc highpass + lowpass loại bỏ dải tần ngoài giọng người và dynaudnorm cân bằng âm lượng
    audio_filters = "highpass=f=80,lowpass=f=7600,dynaudnorm=f=150:g=15"

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", "1",
        "-af", audio_filters,
        str(output_path)
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg trích xuất WAV cho AI thất bại: {proc.stderr}")
    except FileNotFoundError as err:
        raise RuntimeError("Không tìm thấy FFmpeg trên hệ thống.") from err

    return output_path


def get_media_duration_seconds(input_path: Path) -> float:
    """Lấy thời lượng của file media bằng FFprobe hoặc phân tích qua FFmpeg."""
    input_path = Path(input_path).resolve()
    ffmpeg_bin = get_ffmpeg_binary()

    # 1. Thử dùng FFmpeg -i để lấy duration (hoạt động 100% kể cả khi không có ffprobe)
    try:
        proc = subprocess.run(
            [ffmpeg_bin, "-i", str(input_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        combined_output = proc.stderr + proc.stdout
        match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", combined_output)
        if match:
            hours = float(match.group(1))
            minutes = float(match.group(2))
            seconds = float(match.group(3))
            return hours * 3600 + minutes * 60 + seconds
    except (OSError, ValueError):
        pass

    return 0.0
