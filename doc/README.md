# Bộ công cụ: Ghi âm họp (.m4a) → Transcript tiếng Việt chuẩn → Biên bản họp chuyên nghiệp

## Cấu trúc thư mục

```text
Source-Transcript/
├─ AGENTS.md                                      # Quy tắc codebase (tự động áp dụng cho AI Agent)
├─ .agents/
│   └─ skills.json                                # Trỏ trực tiếp thư mục Skill về doc/Skill/
└─ doc/
    ├─ Skill/                                     # Thư mục chuẩn chứa toàn bộ Skill của dự án
    │   ├─ meeting-note/                          # Skill tạo biên bản họp HTML chuẩn KTT (kickoff & weekly)
    │   │   ├─ SKILL.md
    │   │   └─ assets/ (khung_kickoff.html, khung_weekly.html, style.css)
    │   ├─ vietnamese-spellcheck/                 # Skill rà soát chính tả, Unicode & danh xưng Anh/Chị
    │   │   ├─ SKILL.md
    │   │   └─ scripts/ (check_unicode.py)
    │   ├─ mpp-project-reader/                    # Skill đọc & phân tích file tiến độ MS Project (.mpp)
    │   │   ├─ SKILL.md
    │   │   └─ scripts/ (read_mpp.py, project_summary.py)
    │   ├─ meeting-note.skill                     # Bản đóng gói .skill đồng bộ
    │   ├─ vietnamese-spellcheck.skill
    │   └─ mpp-project-reader.skill
    ├─ ghi_am/                                    # Bỏ tất cả file .m4a (hoặc .wma, .mp3, .wav...) vào đây
    ├─ transcripts/                               # Kết quả phiên âm & biên bản họp (tự động tạo)
    │   ├─ <tên file>.txt                         # Transcript có mốc thời gian, đoạn nghi ngờ gắn [??]
    │   ├─ <tên file>.srt                         # Phụ đề chuẩn SRT
    │   ├─ <tên file>_flagged.txt                 # Trích xuất riêng các đoạn [??] kèm khung giờ để nghe lại nhanh
    │   └─ ALL_transcripts.txt                    # Gộp tất cả file để đưa vào tạo biên bản họp
    ├─ transcribe_batch.py                        # Script phiên âm & lọc ảo giác tiếng Việt
    ├─ glossary.txt                               # Thuật ngữ, danh xưng (Anh/Chị) & bảng sửa lỗi nhận dạng
    ├─ meeting_note_prompt.md                     # Quy trình 2 bước: Chuẩn hoá tiếng Việt & Tạo biên bản họp
    └─ README.md
```

## Cài đặt (một lần)

```bash
pip install faster-whisper
# Cài ffmpeg: https://ffmpeg.org (hoặc winget install Gyan.FFmpeg trên Windows)
# Kiểm tra bằng: ffmpeg -version
```

- Có GPU NVIDIA (`cuda`) script sẽ tự động nhận diện và chạy `float16` (nhanh gấp nhiều lần).
- Nếu chạy CPU, dùng `--model medium` nếu máy cấu hình vừa phải, hoặc giữ mặc định `--model large-v3` để có độ chính xác tiếng Việt cao nhất.

## Cách chạy phiên âm

Từ thư mục gốc hoặc thư mục `doc/`:

```bash
python doc/transcribe_batch.py ./doc/ghi_am ./doc/transcripts --glossary ./doc/glossary.txt
# Nếu phòng họp vang hoặc nhiều tiếng ồn nền (điều hoà, quạt):
python doc/transcribe_batch.py ./doc/ghi_am ./doc/transcripts --glossary ./doc/glossary.txt --denoise
```

Các tuỳ chọn nâng cao:
- `--overwrite`: Phiên âm lại cả những file đã có kết quả trong `transcripts/`.
- `--flag-threshold -0.85`: Ngưỡng độ tin cậy `avg_logprob` để gắn cờ `[??]` (mặc định `-0.85`).
- `--no-loudnorm`: Tắt tự động cân bằng âm lượng `dynaudnorm` (mặc định bật để nghe rõ người ngồi xa mic).

## Quy trình chuẩn tạo Biên bản họp (Meeting Note)

1. **Bước 1 - Phiên âm**: Bỏ file `.m4a` vào `doc/ghi_am/` và chạy `transcribe_batch.py` → thu được `ALL_transcripts.txt` và `*_flagged.txt`.
2. **Bước 2 - Chuẩn hoá tiếng Việt & Danh xưng (Gender)**:
   - Áp dụng skill `vietnamese-spellcheck` (trong `doc/Skill/vietnamese-spellcheck/`) và **Bước A** trong `doc/meeting_note_prompt.md`.
   - Đối chiếu nhanh các đoạn gắn `[??]` trong file `*_flagged.txt`.
3. **Bước 3 - Xuất Biên bản họp chuyên nghiệp**:
   - Dùng skill `meeting-note` (trong `doc/Skill/meeting-note/`) để xuất file HTML chuẩn letterhead Công ty TNHH Kiên Thành Tín (`khung_kickoff.html` hoặc `khung_weekly.html`).
   - Kiểm tra danh xưng `Anh` / `Chị` (Gender), Tag bộ phận, số liệu và bảng Action Items trước khi xuất PDF (tối đa 4 trang A4).
