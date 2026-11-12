# -*- coding: utf-8 -*-
"""
video_lyrics_generator.py - Tự động kết hợp Hình ảnh / Video + Âm thanh + Phụ đề Karaoke thành Video MP4 hoàn chỉnh.
Không cần phần mềm bên thứ 3; hỗ trợ tỷ lệ 16:9 (YouTube) và 9:16 (TikTok/Shorts).
Hỗ trợ xuất luôn CapCut PC Draft nếu người dùng muốn mở trực tiếp trên CapCut PC.
"""
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "tools"))

from media_converter import get_ffmpeg_binary


def render_image_lyrics_video(
    image_path: Path,
    audio_path: Path,
    ass_subtitle_path: Path,
    output_video_path: Path,
    aspect_ratio: str = "16:9",
    add_visualizer: bool = False
) -> Path:
    """
    Tạo video từ [Ảnh tĩnh + Nhạc + Phụ đề Karaoke chạy chữ].
    - aspect_ratio: '16:9' (1920x1080) hoặc '9:16' (1080x1920 TikTok/Shorts)
    """
    image_path = Path(image_path).resolve()
    audio_path = Path(audio_path).resolve()
    ass_subtitle_path = Path(ass_subtitle_path).resolve()
    output_video_path = Path(output_video_path).resolve()

    if not image_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file ảnh nền: {image_path}")
    if not audio_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file âm thanh: {audio_path}")
    if not ass_subtitle_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file phụ đề: {ass_subtitle_path}")

    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()

    if aspect_ratio == "9:16":
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    # Thoát ký tự đặc biệt cho FFmpeg filter path (đặc biệt trên Windows có ổ đĩa C: -> C\\:)
    ass_escaped = str(ass_subtitle_path).replace("\\", "/").replace(":", "\\:")

    # Chuỗi filter video
    video_filters = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"ass='{ass_escaped}'"
    )

    cmd = [
        ffmpeg_bin,
        "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-vf", video_filters,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "320k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_video_path)
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg render video ảnh thất bại: {proc.stderr}")

    return output_video_path


def render_video_lyrics_video(
    background_video_path: Path,
    audio_path: Optional[Path],
    ass_subtitle_path: Path,
    output_video_path: Path,
    aspect_ratio: str = "16:9"
) -> Path:
    """
    Tạo video từ [Video clip nền + Nhạc + Phụ đề Karaoke chạy chữ].
    Tự động loop video nền nếu ngắn hơn nhạc.
    """
    background_video_path = Path(background_video_path).resolve()
    ass_subtitle_path = Path(ass_subtitle_path).resolve()
    output_video_path = Path(output_video_path).resolve()

    if not background_video_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy video nền: {background_video_path}")
    if not ass_subtitle_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file phụ đề: {ass_subtitle_path}")

    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()

    if aspect_ratio == "9:16":
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    ass_escaped = str(ass_subtitle_path).replace("\\", "/").replace(":", "\\:")
    video_filters = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"ass='{ass_escaped}'"
    )

    cmd = [
        ffmpeg_bin,
        "-y",
        "-stream_loop", "-1",
        "-i", str(background_video_path)
    ]

    if audio_path and Path(audio_path).is_file():
        cmd.extend(["-i", str(audio_path)])
        cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])
    else:
        cmd.extend(["-map", "0:v:0", "-map", "0:a:0?"])

    cmd.extend([
        "-vf", video_filters,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "320k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_video_path)
    ])

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg render video clip thất bại: {proc.stderr}")

    return output_video_path


def export_capcut_draft_project(
    project_name: str,
    audio_path: Path,
    lines_data: list,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Tạo file cấu trúc draft_content.json của CapCut PC.
    Người dùng có thể copy vào thư mục CapCut Draft để mở trực tiếp trong CapCut PC.
    """
    audio_path = Path(audio_path).resolve()
    if output_dir is None:
        output_dir = BASE_DIR / "output" / "capcut_drafts" / project_name
    output_dir.mkdir(parents=True, exist_ok=True)

    draft_file = output_dir / "draft_content.json"

    # Cấu trúc JSON tương thích CapCut PC Draft
    draft_payload = {
        "id": str(uuid.uuid4()),
        "name": project_name,
        "canvas_config": {"width": 1920, "height": 1080, "ratio": "16:9"},
        "materials": {
            "audios": [{"id": str(uuid.uuid4()), "path": str(audio_path)}],
            "texts": []
        },
        "tracks": [
            {
                "type": "audio",
                "segments": [{"target_timerange": {"start": 0, "duration": 180000000}}]
            },
            {
                "type": "text",
                "segments": []
            }
        ]
    }

    for line in lines_data:
        text_id = str(uuid.uuid4())
        text_content = line.text if hasattr(line, "text") else line.get("text", "")
        start_us = int(round((line.start if hasattr(line, "start") else line.get("start", 0)) * 1_000_000))
        end_us = int(round((line.end if hasattr(line, "end") else line.get("end", 0)) * 1_000_000))

        draft_payload["materials"]["texts"].append({
            "id": text_id,
            "content": f"<color=#FFFFFF><i>{text_content}</i></color>",
            "font_size": 10.0
        })
        draft_payload["tracks"][1]["segments"].append({
            "material_id": text_id,
            "target_timerange": {"start": start_us, "duration": max(1000, end_us - start_us)}
        })

    draft_file.write_text(json.dumps(draft_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return draft_file
