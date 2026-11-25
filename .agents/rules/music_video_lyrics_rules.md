# QUY TẮC BẮT BUỘC KHI XỬ LÝ NHẠC & TẠO VIDEO KARAOKE / LYRICS

Bộ quy tắc này được thiết lập để đảm bảo mọi quy trình tạo video âm nhạc, chạy lời bài hát (lyrics/karaoke), xử lý phông chữ, chữ ký và hashtag trong dự án đều đạt chuẩn mực thẩm mỹ cao nhất và không bị lặp lại lỗi.

---

## 1. NGUYÊN TẮC KHỚP THỜI GIAN LỜI HÁT (TIMING & LIP-SYNC ACCURACY)
1. **Ca sĩ chưa hát - Tuyệt đối không chạy lời trước**:
   - Khi bài hát có đoạn dạo đầu (intro) của nhạc cụ (piano, guitar, trống...), màn hình chỉ hiển thị ảnh nền và dải hashtag ở đỉnh, **tuyệt đối không hiển thị trước câu hát đầu tiên**.
   - Lời bài hát câu đầu tiên chỉ được xuất hiện đúng tại thời điểm ca sĩ cất giọng thực tế (onset timestamp).
2. **Xác định mốc thời gian bằng AI & Audio Onset**:
   - Luôn sử dụng mô hình AI (`faster-whisper`) hoặc phân tích dải sóng âm trên file WAV mono 16kHz đã lọc sạch để lấy mốc thời gian chính xác của câu đầu tiên và từng từ, không dùng mốc thời gian ước đoán hay file LRC trôi nổi chưa kiểm chứng.

---

## 2. NGUYÊN TẮC CHỮ KÝ BẢN QUYỀN (SIGNATURE POLICY)
1. **Ảnh nền đã có sẵn chữ ký mộc**:
   - Nếu ảnh gốc (`input/images/`) đã có sẵn chữ ký mộc của tác giả/thương hiệu ở góc dưới bên phải (`right bottom`), **TUYỆT ĐỐI KHÔNG CHÈN THÊM CHỮ KÝ** để tránh trùng lặp, đè chữ làm xấu khung hình.
2. **Ảnh nền chưa có chữ ký**:
   - Chỉ chèn thêm chữ ký khi ảnh gốc hoàn toàn chưa có chữ ký.
   - Vị trí bắt buộc: Góc dưới bên phải (**Right-Bottom**, ASS Alignment 3).
   - Định dạng: Chữ thẳng đứng, phông Arial thanh mảnh (~24px), dãn cách chữ rộng (`Spacing 3.5`), độ mờ nhẹ ~75-80% (`&H30FFFFFF`) trang nhã.

---

## 3. NGUYÊN TẮC DẢI HASHTAGS MẠNG XÃ HỘI (HASHTAGS POLICY)
1. **Luôn giữ lại dải Hashtags**:
   - Dải hashtags mạng xã hội (`#...`) hoàn toàn độc lập với chữ ký. Khi không chèn chữ ký (hoặc bỏ chữ ký), **dải hashtags VẪN BẮT BUỘC PHẢI CÓ** trên video.
2. **Vị trí & Định dạng Bố cục**:
   - **Bố cục & Phông chữ đồng bộ (Top-Left, ASS Alignment 7)**: Mỗi hashtag nằm trên một dòng riêng biệt, canh lề trái thẳng hàng (`MarginL` ~50px, `MarginV` ~55-75px). Sử dụng **cùng phông chữ thuộc nhóm Script (như `Dancing Script`) với lời bài hát, in nghiêng (Italic) và CỠ CHỮ BẰNG NHAU với lời bài hát (mặc định chuẩn 38px)**, màu xám mờ tinh tế (`&H25F0E0D0`) để tạo sự đồng bộ thẩm mỹ, thoáng đãng và bay bổng cho video.

---

## 4. QUY CHUẨN PHÔNG CHỮ & CỠ CHỮ (TYPOGRAPHY - NHÓM SCRIPT)
1. **Bắt buộc dùng phông nhóm Script (Thư pháp / Chữ thảo)**:
   - Với các ca khúc trữ tình, tâm trạng, ballad, acoustic hoặc cover: Phông chữ lời bài hát bắt buộc thuộc **nhóm Script** nghệ thuật mềm mại (mặc định ưu tiên: `Dancing Script`).
2. **Đảm bảo 100% Tiếng Việt có dấu**:
   - Font chữ được chọn phải hỗ trợ đầy đủ bộ ký tự tiếng Việt có dấu chuẩn Unicode dựng sẵn (NFC). Tuyệt đối không dùng các font script tiếng Anh chưa Việt hoá (như Segoe Script) gây lỗi rớt dấu hoặc hiển thị ô vuông.
   - Thư mục lưu trữ font chuẩn: `tools/fonts/` (ví dụ: `tools/fonts/DancingScript-Regular.ttf`).
3. **Cỡ chữ & Hiệu ứng Karaoke**:
   - Kích thước: Cỡ chữ dạng caption social thanh lịch chuẩn **38px** (tối ưu độ rõ ràng cho font Script nét thảo, không bị quá nhỏ và không choán khung hình).
   - Viền & Đổ bóng: Viền mỏng 1.8-2.0px, shadow mềm 1.2-1.5px để nổi bật trên nền tối.
   - Đổi màu karaoke: Chuyển màu vàng neon / hổ phách (`&H0000D7FF`) mượt mà theo từng từ ca sĩ hát.

---

## 5. NGUYÊN TẮC KỸ THUẬT FFMPEG & ZERO HARDCODING
1. **Luôn gắn `fontsdir` cho bộ lọc ASS của FFmpeg**:
   - Khi chạy lệnh FFmpeg với phụ đề `.ass`, bắt buộc kèm tham số `fontsdir` trỏ về thư mục `tools/fonts/`:
     ```python
     ass_filter = f"ass='{ass_escaped}':fontsdir='{fonts_dir_esc}'"
     ```
     để libass luôn tìm thấy font `Dancing Script` cục bộ ngay cả khi máy tính chưa cài đặt font vào hệ thống Windows Fonts.
2. **Chuyển đổi âm thanh MP3 320kbps**:
   - Luôn tự động convert file video/audio nặng sang MP3 320kbps gọn nhẹ trước khi xử lý.
3. **Tuân thủ chính sách File dung lượng lớn**:
   - Toàn bộ file MP3, WAV, MP4 chỉ lưu tại local, không commit lên Git; luôn kiểm tra qua `tools/check_large_files.py`.
   - Tuyệt đối không hardcode đường dẫn ổ đĩa vật lý, luôn dùng `Path(__file__).resolve().parent`.
