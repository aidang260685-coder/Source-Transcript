# -*- coding: utf-8 -*-
"""
video_lyrics_generator.py - Tự động kết hợp Hình ảnh / Video + Âm thanh + Phụ đề Karaoke thành Video MP4 hoàn chỉnh.
Không cần phần mềm bên thứ 3; hỗ trợ tỷ lệ 16:9 (YouTube) và 9:16 (TikTok/Shorts).
Hỗ trợ xuất luôn CapCut PC Draft nếu người dùng muốn mở trực tiếp trên CapCut PC.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import List, Optional, Union

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "tools"))

from media_converter import get_ffmpeg_binary


def get_audio_duration(audio_path: Path, ffmpeg_bin: Path) -> float:
    """Lấy thời lượng âm thanh bằng FFmpeg."""
    cmd = [str(ffmpeg_bin), "-i", str(audio_path)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if m:
        hours, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
        return hours * 3600 + mins * 60 + secs
    return 300.0


def render_image_lyrics_video(
    image_path: Union[Path, str, List[Union[Path, str]]],
    audio_path: Path,
    ass_subtitle_path: Path,
    output_video_path: Path,
    aspect_ratio: str = "16:9",
    bg_mode: str = "blur_padding",
    add_visualizer: bool = False
) -> Path:
    """
    Tạo video từ [Ảnh tĩnh (1 hoặc nhiều ảnh) + Nhạc + Phụ đề Karaoke chạy chữ].
    - image_path: 1 ảnh hoặc danh sách nhiều ảnh. Nếu nhiều ảnh, tự động chuyển cảnh hòa tan (Crossfade).
    - aspect_ratio: '16:9' (1920x1080) hoặc '9:16' (1080x1920 TikTok/Shorts/Zalo)
    - bg_mode:
        + 'blur_padding': Hiệu ứng CapCut/TikTok nền mờ (ảnh gốc ở giữa sắc nét, nền sau mờ mịn)
        + 'crop': Phóng to ảnh cắt vừa khít toàn màn hình
    """
    if isinstance(image_path, (list, tuple)):
        images = [Path(p).resolve() for p in image_path if Path(p).is_file()]
    else:
        images = [Path(image_path).resolve()] if Path(image_path).is_file() else []

    if not images:
        raise FileNotFoundError(f"Không tìm thấy file ảnh nền hợp lệ: {image_path}")

    audio_path = Path(audio_path).resolve()
    ass_subtitle_path = Path(ass_subtitle_path).resolve()
    output_video_path = Path(output_video_path).resolve()

    if not audio_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file âm thanh: {audio_path}")
    if not ass_subtitle_path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file phụ đề: {ass_subtitle_path}")

    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()

    if aspect_ratio == "3:4":
        width, height = 1080, 1440
    elif aspect_ratio == "9:16":
        width, height = 1080, 1920
    else:
        width, height = 1920, 1080

    # Thoát ký tự đặc biệt cho FFmpeg filter path (đặc biệt trên Windows có ổ đĩa C: -> C\\:)
    ass_escaped = str(ass_subtitle_path).replace("\\", "/").replace(":", "\\:")

    # TRƯỜNG HỢP 1: DUY NHẤT 1 ẢNH (Tối ưu siêu tốc với pre-composited frame)
    if len(images) == 1:
        img_single = images[0]
        if bg_mode == "blur_padding":
            temp_comp_bg = output_video_path.parent / f"_temp_bg_{width}x{height}.jpg"
            filter_once = (
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},boxblur=25:5[bg];"
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
            )
            cmd_prep = [
                str(ffmpeg_bin), "-y", "-loglevel", "error",
                "-i", str(img_single),
                "-filter_complex", filter_once,
                "-vframes", "1",
                str(temp_comp_bg)
            ]
            proc_prep = subprocess.run(cmd_prep, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if proc_prep.returncode != 0:
                raise RuntimeError(f"Tạo ảnh nền composited thất bại: {proc_prep.stderr}")

            cmd = [
                str(ffmpeg_bin), "-y", "-loglevel", "error",
                "-loop", "1", "-i", str(temp_comp_bg),
                "-i", str(audio_path),
                "-vf", f"ass='{ass_escaped}'",
                "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "18",
                "-c:a", "aac", "-b:a", "320k", "-pix_fmt", "yuv420p", "-shortest",
                str(output_video_path)
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if temp_comp_bg.is_file():
                temp_comp_bg.unlink(missing_ok=True)
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg render video ảnh thất bại: {proc.stderr}")
        else:
            video_filters = (
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},"
                f"ass='{ass_escaped}'"
            )
            cmd = [
                str(ffmpeg_bin), "-y", "-loglevel", "error",
                "-loop", "1", "-i", str(img_single),
                "-i", str(audio_path),
                "-vf", video_filters,
                "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "18",
                "-c:a", "aac", "-b:a", "320k", "-pix_fmt", "yuv420p", "-shortest",
                str(output_video_path)
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg render video ảnh thất bại: {proc.stderr}")

        return output_video_path

    # TRƯỜNG HỢP 2: NHIỀU ẢNH (Tự động chuyển cảnh Crossfade Slideshow hòa tan mờ)
    num_imgs = len(images)
    total_dur = get_audio_duration(audio_path, ffmpeg_bin)
    interval = total_dur / num_imgs
    xfade_dur = min(1.5, interval / 2)

    # 1. Tạo các slide tĩnh đã xử lý blur_padding hoặc crop
    temp_slides: List[Path] = []
    for idx, img in enumerate(images):
        slide_p = output_video_path.parent / f"_temp_slide_{idx}_{width}x{height}.jpg"
        temp_slides.append(slide_p)
        if bg_mode == "blur_padding":
            filter_once = (
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},boxblur=25:5[bg];"
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
            )
        else:
            filter_once = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"

        cmd_slide = [
            str(ffmpeg_bin), "-y", "-loglevel", "error",
            "-i", str(img),
            "-filter_complex", filter_once,
            "-vframes", "1",
            str(slide_p)
        ]
        proc_s = subprocess.run(cmd_slide, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if proc_s.returncode != 0:
            raise RuntimeError(f"Tạo slide composited {idx} thất bại: {proc_s.stderr}")

    # 2. Xây dựng filter_complex lồng ghép các lớp ảnh chuyển cảnh mờ dần
    fc_parts = []
    curr_base = "0:v"
    for idx in range(1, num_imgs):
        start_time = idx * interval
        fc_parts.append(f"[{idx}:v]format=yuva420p,fade=t=in:st={start_time:.2f}:d={xfade_dur:.2f}:alpha=1[v_fade_{idx}]")
        fc_parts.append(f"[{curr_base}][v_fade_{idx}]overlay=0:0[v_base_{idx}]")
        curr_base = f"v_base_{idx}"

    fc_parts.append(f"[{curr_base}]ass='{ass_escaped}'[vout]")
    full_fc = "; ".join(fc_parts)

    cmd_multi = [str(ffmpeg_bin), "-y", "-loglevel", "error"]
    for slide in temp_slides:
        cmd_multi.extend(["-loop", "1", "-t", f"{total_dur + 5:.2f}", "-i", str(slide)])

    cmd_multi.extend([
        "-i", str(audio_path),
        "-filter_complex", full_fc,
        "-map", "[vout]",
        "-map", f"{num_imgs}:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "320k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_video_path)
    ])

    proc_multi = subprocess.run(cmd_multi, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)

    # Dọn dẹp slide tạm
    for slide in temp_slides:
        if slide.is_file():
            slide.unlink(missing_ok=True)

    if proc_multi.returncode != 0:
        raise RuntimeError(f"FFmpeg render multi-image slideshow thất bại: {proc_multi.stderr}")

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

    if aspect_ratio == "3:4":
        width, height = 1080, 1440
    elif aspect_ratio == "9:16":
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
