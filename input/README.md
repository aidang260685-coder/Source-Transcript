# THƯ MỤC ĐẦU VÀO (INPUT ASSETS)

Đặt các tệp tư liệu cần xử lý vào các thư mục tương ứng bên dưới:

```
input/
├── music/       # Chứa file bài hát (.mp3, .wav, .flac, .m4a) hoặc video gốc (.mp4)
├── images/      # Chứa file ảnh nền (.jpg, .png) làm hình nền video
└── lyrics/      # Chứa file lời bài hát (.txt) nếu bạn đã có sẵn lời chuẩn
```

---

## CÁCH CHẠY NHANH:

1. **Thả file nhạc vào `input/music/`** (ví dụ: `input/music/bai_hat.mp3`)
2. **Thả ảnh nền vào `input/images/`** (ví dụ: `input/images/anh_nen.jpg`)
3. **Thả lời bài hát vào `input/lyrics/`** (ví dụ: `input/lyrics/loi_bai_hat.txt` - tuỳ chọn)
4. **Chạy lệnh**:
   ```powershell
   # Video khổ ngang 16:9 cho YouTube
   python3.12 tools/process_music.py -i input/music/bai_hat.mp3 -img input/images/anh_nen.jpg -t "Tên Bài Hát" -a "Ca Sĩ" -r 16:9

   # Video khổ dọc 9:16 cho TikTok / Reels / Shorts
   python3.12 tools/process_music.py -i input/music/bai_hat.mp3 -img input/images/anh_nen.jpg -t "Tên Bài Hát" -a "Ca Sĩ" -r 9:16
   ```

Toàn bộ video thành phẩm và các file phụ đề Karaoke chữ nghiêng mềm mại (`.ass`, `.lrc`, `.srt`) sẽ tự động được xuất ra tại thư mục:
👉 `output/music/<tên_bài_hát>/`
