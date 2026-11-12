# -*- coding: utf-8 -*-
"""
process_music.py - Bộ công cụ CLI đa năng:
1. Chuyển đổi Video/Audio sang MP3 chất lượng cao.
2. Trích xuất lời bài hát đồng bộ (Sync Lyrics: Standard LRC, Enhanced LRC, Karaoke ASS, SRT, JSON).
3. Tự động kết hợp [Hình ảnh / Video nền] + [Nhạc MP3] + [Caption Karaoke] thành Video MP4 hoàn chỉnh.
4. Tùy chọn xuất CapCut PC Draft.
"""
import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "tools"))

from media_converter import (
    convert_to_mp3,
    extract_clean_wav_for_ai,
    get_media_duration_seconds,
    is_ffmpeg_available
)
from sync_lyrics_engine import (
    LineSegment,
    export_enhanced_lrc,
    export_json_timeline,
    export_karaoke_ass,
    export_srt,
    export_standard_lrc,
    transcribe_and_align_lyrics
)
from video_lyrics_generator import (
    export_capcut_draft_project,
    render_image_lyrics_video,
    render_video_lyrics_video
)


def auto_detect_inputs(
    input_file: Path = None,
    image_bg: Path = None,
    lyrics_file: Path = None
):
    """
    Tự động ghép cặp thông minh giữa file nhạc (input/music/) và hình ảnh (input/images/):
    1. Cơ chế 1 (Auto Single-Pair): Nếu mỗi thư mục chỉ có 1 file duy nhất -> Tự động ghép thành 1 cặp.
    2. Cơ chế 2 (Matching Name): Nếu có file cùng tên (ví dụ: song.mp3 và song.jpg) -> Ghép đôi chuẩn xác.
    3. Cơ chế 3: Nạp theo tham số được người dùng chỉ định cụ thể.
    """
    valid_audio_exts = {".mp3", ".wav", ".m4a", ".webm", ".flac", ".ogg", ".mp4", ".mkv", ".aac"}
    valid_image_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    valid_lyrics_exts = {".txt", ".lrc"}

    music_dir = BASE_DIR / "input" / "music"
    images_dir = BASE_DIR / "input" / "images"
    lyrics_dir = BASE_DIR / "input" / "lyrics"

    music_files = [f for f in music_dir.glob("*") if f.is_file() and f.suffix.lower() in valid_audio_exts]
    image_files = [f for f in images_dir.glob("*") if f.is_file() and f.suffix.lower() in valid_image_exts]
    text_files = [f for f in lyrics_dir.glob("*") if f.is_file() and f.suffix.lower() in valid_lyrics_exts]

    # 1. Xác định file nhạc
    chosen_input = None
    if input_file:
        p_in = Path(input_file)
        if p_in.is_file():
            chosen_input = p_in.resolve()
        elif (music_dir / p_in.name).is_file():
            chosen_input = (music_dir / p_in.name).resolve()
        else:
            sys.exit(f"❌ Lỗi: Không tìm thấy file nhạc: {input_file} (kiểm tra cả input/music/)")
    else:
        if len(music_files) == 1:
            chosen_input = music_files[0].resolve()
            print(f"💡 [TỰ ĐỘNG GHÉP CẶP] Phát hiện 1 bài nhạc duy nhất trong input/music/: {chosen_input.name}")
        elif len(music_files) > 1:
            print("⚠️ Phát hiện nhiều file nhạc trong input/music/:")
            for idx, mf in enumerate(music_files, 1):
                print(f"   [{idx}] {mf.name}")
            sys.exit("👉 Vui lòng thêm tham số -i \"<tên_file>\" để chọn bài hát cần xử lý.")
        else:
            sys.exit("❌ Thư mục input/music/ chưa có file nhạc nào. Vui lòng copy file nhạc vào input/music/.")

    # 2. Tự động nhận diện ảnh ghép cặp
    chosen_img = None
    if image_bg:
        p_img = Path(image_bg)
        if p_img.is_file():
            chosen_img = p_img.resolve()
        elif (images_dir / p_img.name).is_file():
            chosen_img = (images_dir / p_img.name).resolve()
    else:
        # Tìm ảnh trùng tên trước
        matching_imgs = [img for img in image_files if img.stem.lower() == chosen_input.stem.lower()]
        if matching_imgs:
            chosen_img = matching_imgs[0].resolve()
            print(f"💡 [TỰ ĐỘNG GHÉP CẶP] Tìm thấy ảnh trùng tên trong input/images/: {chosen_img.name}")
        elif len(image_files) == 1:
            chosen_img = image_files[0].resolve()
            print(f"💡 [TỰ ĐỘNG GHÉP CẶP] Tự động bắt cặp với bức ảnh duy nhất trong input/images/: {chosen_img.name}")
        elif len(image_files) > 1:
            chosen_img = image_files[0].resolve()
            print(f"💡 [TỰ ĐỘNG GHÉP CẶP] Phát hiện {len(image_files)} ảnh trong input/images/. Mặc định ghép với ảnh đầu tiên: {chosen_img.name}")
            print(f"   (👉 Anh có thể dùng tham số -img \"{image_files[1].name}\" nếu muốn đổi ảnh khác)")

    # 3. Tự động nhận diện file lời (lyrics) nếu có
    chosen_lyr = None
    if lyrics_file:
        p_lyr = Path(lyrics_file)
        if p_lyr.is_file():
            chosen_lyr = p_lyr.resolve()
        elif (lyrics_dir / p_lyr.name).is_file():
            chosen_lyr = (lyrics_dir / p_lyr.name).resolve()
    else:
        matching_lyrs = [txt for txt in text_files if txt.stem.lower() == chosen_input.stem.lower()]
        if matching_lyrs:
            chosen_lyr = matching_lyrs[0].resolve()
            print(f"💡 [TỰ ĐỘNG GHÉP CẶP] Tìm thấy file lời trùng tên trong input/lyrics/: {chosen_lyr.name}")
        elif len(text_files) == 1:
            chosen_lyr = text_files[0].resolve()
            print(f"💡 [TỰ ĐỘNG GHÉP CẶP] Tự động bắt cặp với file lời text duy nhất: {chosen_lyr.name}")

    return chosen_input, chosen_img, chosen_lyr


def run_pipeline(
    input_file: Path = None,
    image_bg: Path = None,
    video_bg: Path = None,
    lyrics_file: Path = None,
    title: str = "Tên Bài Hát",
    artist: str = "Ca Sĩ",
    aspect_ratio: str = "9:16",
    bg_mode: str = "blur_padding",
    style_preset: str = "soft_italic",
    font_name: str = "Georgia",
    italic: bool = True,
    signature: str = None,
    hashtags: str = None,
    output_dir: Path = None,
    export_capcut: bool = False
):
    """Quy trình tự động khép kín với cơ chế ghép cặp thông minh."""
    input_file, image_bg, lyrics_file = auto_detect_inputs(input_file, image_bg, lyrics_file)

    if output_dir is None:
        song_dir = BASE_DIR / "output" / "music" / input_file.stem
    else:
        song_dir = Path(output_dir).resolve()

    # Cấu trúc thư mục chuẩn hoá (Standardized Output Directory Structure)
    dir_mp3 = song_dir / "mp3"
    dir_lyrics = song_dir / "lyrics"
    dir_karaoke = song_dir / "karaoke"
    dir_videos = song_dir / "videos"
    dir_capcut = song_dir / "capcut"

    for d in (dir_mp3, dir_lyrics, dir_karaoke, dir_videos, dir_capcut):
        d.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🎵 HỆ THỐNG XỬ LÝ NHẠC & TỰ ĐỘNG TẠO VIDEO KARAOKE ĐỒNG BỘ")
    print(f"📁 Tệp đầu vào: {input_file.name}")
    if signature:
        print(f"✍️  Chữ ký bản quyền: {signature}")
    if hashtags:
        print(f"🏷️  Hashtags: {hashtags}")
    print(f"🎯 Thư mục xuất chuẩn: {song_dir}")
    print("=" * 70)

    # 1. Chuyển đổi sang MP3
    print("\n[BƯỚC 1/3] Chuẩn hoá định dạng âm thanh sang MP3 (320kbps)...")
    mp3_path = dir_mp3 / f"{input_file.stem}.mp3"
    wav_ai_path = dir_mp3 / f"{input_file.stem}_16k.wav"

    if is_ffmpeg_available():
        convert_to_mp3(input_file, mp3_path, bitrate="320k")
        print(f"   ✓ [mp3/] Đã tạo file MP3 320kbps: {mp3_path.name}")
        extract_clean_wav_for_ai(input_file, wav_ai_path)
        print(f"   ✓ [mp3/] Đã tạo WAV mono lọc sạch cho AI: {wav_ai_path.name}")
    else:
        print("   ⚠️ Lưu ý: Chưa phát hiện binary ffmpeg.exe trong hệ thống.")
        if input_file.suffix.lower() == ".mp3":
            mp3_path = input_file
        wav_ai_path = input_file

    # 2. Đọc lời gốc (nếu có) và căn chỉnh mốc thời gian
    print("\n[BƯỚC 2/3] Trích xuất & căn chỉnh mốc thời gian lời bài hát (Sync Lyrics)...")
    ref_lyrics = None
    if lyrics_file and Path(lyrics_file).is_file():
        ref_lyrics = Path(lyrics_file).read_text(encoding="utf-8")
        print(f"   ✓ Đã nạp lời bài hát gốc từ: {Path(lyrics_file).name}")

    segments = transcribe_and_align_lyrics(
        wav_ai_path,
        reference_lyrics=ref_lyrics,
        language="vi"
    )
    print(f"   ✓ Đã căn chỉnh thành công {len(segments)} dòng phụ đề có mốc thời gian từng từ.")

    # Xuất các chuẩn định dạng vào thư mục chuyên biệt
    out_lrc = dir_lyrics / f"{input_file.stem}.lrc"
    out_enhanced_lrc = dir_lyrics / f"{input_file.stem}_enhanced.lrc"
    out_ass = dir_karaoke / f"{input_file.stem}_karaoke.ass"
    out_srt = dir_lyrics / f"{input_file.stem}.srt"
    out_json = dir_lyrics / f"{input_file.stem}_timeline.json"

    res_str = "1080x1920" if aspect_ratio == "9:16" else "1920x1080"
    out_lrc.write_text(export_standard_lrc(segments, title, artist), encoding="utf-8")
    out_enhanced_lrc.write_text(export_enhanced_lrc(segments, title, artist), encoding="utf-8")
    out_ass.write_text(
        export_karaoke_ass(
            segments,
            title,
            resolution=res_str,
            style_preset=style_preset,
            font_name=font_name,
            italic=italic,
            signature=signature,
            hashtags=hashtags
        ),
        encoding="utf-8"
    )
    out_srt.write_text(export_srt(segments), encoding="utf-8")
    out_json.write_text(export_json_timeline(segments), encoding="utf-8")

    # Xuất file caption_social.txt tiện sao chép khi đăng TikTok/Zalo
    caption_txt = f"{title} - {artist}\n"
    if segments:
        quote_line = segments[len(segments)//2].text if len(segments) > 2 else segments[0].text
        caption_txt += f"\"{quote_line}\" 🎵\n\n"
    if signature:
        caption_txt += f"Cre: {signature}\n"
    default_tags = hashtags or "#nhachay #tamtrang #cover #nhacbuon #xuhuong #fyp #tiktokmusic"
    caption_txt += f"----------------------------------------\n{default_tags}\n"
    out_caption = dir_videos / "caption_social.txt"
    out_caption.write_text(caption_txt, encoding="utf-8")
    print(f"   ✓ [videos/] File Caption mạng xã hội: {out_caption.name}")

    print(f"   ✓ [lyrics/] Standard LRC: {out_lrc.name}")
    print(f"   ✓ [lyrics/] Enhanced LRC (Word-level): {out_enhanced_lrc.name}")
    print(f"   ✓ [lyrics/] SRT Subtitle: {out_srt.name}")
    print(f"   ✓ [lyrics/] JSON Timeline: {out_json.name}")
    print(f"   ✓ [karaoke/] Karaoke ASS (Hiệu ứng \\k đổi màu): {out_ass.name}")

    if export_capcut:
        draft_f = export_capcut_draft_project(input_file.stem, mp3_path, segments, output_dir=dir_capcut)
        print(f"   ✓ [capcut/] CapCut PC Draft: {draft_f.name}")

    # 3. Render Video hoàn chỉnh (nếu có ảnh hoặc video nền)
    print("\n[BƯỚC 3/3] Xuất Video hoàn chỉnh...")
    out_video = dir_videos / f"{input_file.stem}_karaoke_{aspect_ratio.replace(':', '_')}.mp4"

    if not is_ffmpeg_available():
        print("   ⚠️ Không thể render video trực tiếp do thiếu FFmpeg binary.")
        print("   👉 Bạn có thể tải ffmpeg.exe thả vào thư mục 'tools/' hoặc import file .ass vào CapCut/Premiere.")
        return

    if image_bg and Path(image_bg).is_file():
        print(f"   🎬 Đang render video từ ảnh nền [{Path(image_bg).name}] ({aspect_ratio}, chế độ: {bg_mode})...")
        render_image_lyrics_video(
            image_path=Path(image_bg),
            audio_path=mp3_path,
            ass_subtitle_path=out_ass,
            output_video_path=out_video,
            aspect_ratio=aspect_ratio,
            bg_mode=bg_mode
        )
        print(f"   🎉 THÀNH CÔNG! [videos/] Video Karaoke: {out_video.name}")

    elif video_bg and Path(video_bg).is_file():
        print(f"   🎬 Đang render video từ video nền [{Path(video_bg).name}] ({aspect_ratio})...")
        render_video_lyrics_video(
            background_video_path=Path(video_bg),
            audio_path=mp3_path,
            ass_subtitle_path=out_ass,
            output_video_path=out_video,
            aspect_ratio=aspect_ratio
        )
        print(f"   🎉 THÀNH CÔNG! [videos/] Video Karaoke: {out_video.name}")
    else:
        print("   ℹ️ Không có ảnh/video nền được chỉ định. Đã xuất toàn bộ file audio MP3 và phụ đề Karaoke.")

    print("\n" + "=" * 70)
    print(f"✅ HOÀN TẤT TOÀN BỘ TIẾN TRÌNH! Kiểm tra thư mục: {song_dir}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Bộ công cụ Convert Media & Tự động tạo Video Karaoke chạy chữ theo nhạc."
    )
    parser.add_argument("--input", "-i", default=None, help="Đường dẫn file video/audio đầu vào (bỏ trống để tự động ghép cặp trong input/music/)")
    parser.add_argument("--image", "-img", default=None, help="Đường dẫn file ảnh nền JPG/PNG (bỏ trống để tự động ghép cặp trong input/images/)")
    parser.add_argument("--video-bg", "-vbg", default=None, help="Đường dẫn file video clip nền (MP4)")
    parser.add_argument("--lyrics", "-l", default=None, help="Đường dẫn file text chứa lời bài hát gốc (nếu có)")
    parser.add_argument("--title", "-t", default="Tên Bài Hát", help="Tiêu đề bài hát")
    parser.add_argument("--artist", "-a", default="Ca Sĩ", help="Tên ca sĩ / nghệ sĩ")
    parser.add_argument("--signature", "--sig", default=None, help="Chữ ký / Watermark bản quyền (ví dụ: 'H O A N G A N')")
    parser.add_argument("--hashtags", "--tag", default=None, help="Dải hashtag trên video và caption (ví dụ: '#saicuasai #cover #nhachay')")
    parser.add_argument("--ratio", "-r", default="9:16", choices=["9:16", "16:9"], help="Tỷ lệ khung hình video: 9:16 (TikTok, Zalo, Reels, Shorts) hoặc 16:9 (YouTube)")
    parser.add_argument("--bg-mode", default="blur_padding", choices=["blur_padding", "crop"], help="Chế độ xử lý ảnh nền: blur_padding (nền mờ CapCut/TikTok giữ trọn vẹn ảnh) hoặc crop (cắt vừa khít)")
    parser.add_argument("--style", default="soft_italic", choices=["soft_italic", "poetic", "handwritten", "modern_italic"], help="Phong cách phụ đề lyric (mặc định: soft_italic)")
    parser.add_argument("--font", default="Georgia", help="Tên phông chữ nghệ thuật cho lyric (mặc định: Georgia)")
    parser.add_argument("--no-italic", action="store_true", help="Tắt chữ nghiêng (mặc định luôn bật chữ nghiêng mềm mại)")
    parser.add_argument("--outdir", "-o", default=None, help="Thư mục xuất kết quả")
    parser.add_argument("--capcut", action="store_true", help="Xuất thêm file project CapCut PC draft")

    args = parser.parse_args()

    run_pipeline(
        input_file=Path(args.input) if args.input else None,
        image_bg=Path(args.image) if args.image else None,
        video_bg=Path(args.video_bg) if args.video_bg else None,
        lyrics_file=Path(args.lyrics) if args.lyrics else None,
        title=args.title,
        artist=args.artist,
        aspect_ratio=args.ratio,
        bg_mode=args.bg_mode,
        style_preset=args.style,
        font_name=args.font,
        italic=not args.no_italic,
        signature=args.signature,
        hashtags=args.hashtags,
        output_dir=Path(args.outdir) if args.outdir else None,
        export_capcut=args.capcut
    )


if __name__ == "__main__":
    main()
