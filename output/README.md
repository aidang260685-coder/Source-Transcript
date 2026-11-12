# QUY ƯỚC CẤU TRÚC THƯ MỤC XUẤT BẢN CHUẨN (`output/`)

Thư mục `output/` là **Cổng xuất bản chính thức (Publishable Gate)** của hệ thống. Toàn bộ các sản phẩm hoàn chỉnh đã qua kiểm định hoặc render tự động được phân chia theo cấu trúc phân tầng chuẩn hoá dưới đây:

```
output/
│
├── meeting_notes/          # [PHÂN HỆ 1] BIÊN BẢN HỌP CÔNG TY ĐÃ KIỂM ĐỊNH (VERIFIED)
│   ├── Bien_Ban_Hop_[TieuDe]_[Ngay]_Verified.html
│   └── Bien_Ban_Hop_[TieuDe]_[Ngay]_Verified.pdf
│
└── music/                  # [PHÂN HỆ 2] NHẠC, PHỤ ĐỀ KARAOKE & VIDEO RENDER HOÀN CHỈNH
    └── <tên_bài_hát>/      # Mỗi bài hát là một không gian dự án độc lập:
        │
        ├── mp3/            # 1. Âm thanh chuẩn nén
        │   ├── <tên>.mp3   # File MP3 chất lượng cao 320kbps (Stereo)
        │   └── <tên>_16k.wav # File WAV mono đã lọc sạch dải tần cho AI
        │
        ├── lyrics/         # 2. Các định dạng phụ đề lời bài hát
        │   ├── <tên>.lrc             # Standard LRC (hiển thị câu trên Zing MP3, Spotify)
        │   ├── <tên>_enhanced.lrc    # Enhanced LRC (chữ chạy từng từ)
        │   ├── <tên>.srt             # Subtitle SRT chuẩn
        │   └── <tên>_timeline.json   # Dữ liệu timeline JSON chi tiết
        │
        ├── karaoke/        # 3. Phụ đề hiệu ứng Karaoke chuyên nghiệp
        │   └── <tên>_karaoke.ass     # File .ass chứa mã \k đổi màu chữ theo nhịp hát ca sĩ
        │
        ├── videos/         # 4. Video MP4 hoàn chỉnh tự động xuất qua FFmpeg
        │   ├── <tên>_karaoke_16_9.mp4  # Khổ ngang 1080p cho YouTube / Facebook
        │   └── <tên>_karaoke_9_16.mp4  # Khổ dọc 1080p cho TikTok / Shorts / Reels
        │
        └── capcut/         # 5. File dự án tích hợp phần mềm bên thứ 3
            └── draft_content.json      # Mở trực tiếp trên CapCut PC mà không cần gõ sub
```

---

## NGUYÊN TẮC QUẢN LÝ
1. **Không xáo trộn định dạng**: Mỗi file đầu ra được đặt đúng thư mục chức năng chuyên biệt (`mp3/`, `lyrics/`, `karaoke/`, `videos/`, `capcut/`).
2. **Bảo mật & Dung lượng lớn**: Các file video/audio lớn được kiểm soát qua `.gitignore` và `tools/check_large_files.py`.
3. **Truy vết tự hành**: Mọi lần chạy của hệ thống đều ghi nhật ký tương ứng vào `runs/<run_id>.jsonl`.
