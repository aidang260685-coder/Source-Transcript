# CẤU HÌNH AI AGENT - DỰ ÁN SOURCE-TRANSCRIPT

Toàn bộ quy tắc cốt lõi của dự án được định nghĩa chi tiết tại [`AGENTS.md`](./AGENTS.md). AI Agent khi làm việc trong workspace này bắt buộc phải tuân thủ:

## 1. NGUYÊN TẮC BẢO MẬT & BẢO VỆ DỮ LIỆU (HIGHEST PRIORITY)
- Mọi mật khẩu, tài khoản, Personal Access Token (PAT), Secret Key hoặc thông tin người dùng chia sẻ **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ Ý CHIA SẺ CHO BẤT KỲ AGENT AI NÀO KHÁC**.
- Bất kỳ thao tác chuyển giao, chia sẻ hay cấp quyền nào đều **BẮT BUỘC PHẢI HỎI VÀ ĐƯỢC NGƯỜI DÙNG CONFIRM TRỰC TIẾP**.
- Tuyệt đối không commit bí mật đăng nhập vào git hoặc lưu trong mã nguồn mở.

## 2. QUY ĐỊNH TUYỆT ĐỐI KHÔNG HARDCODE (ZERO HARDCODING POLICY)
- **CẤM hardcode đường dẫn tuyệt đối**: Tuyệt đối không hardcode ổ đĩa vật lý (`C:\`, `D:\`, `/home/`). Luôn dùng đường dẫn động `Path(__file__).resolve().parent.parent` hoặc biến môi trường `BASE_DIR`.
- **CẤM hardcode thông tin bí mật**: Không ghi token, mật khẩu, API keys vào file mã nguồn hoặc cấu hình commit lên Git. Luôn nạp qua biến môi trường hoặc `.env` (đã có trong `.gitignore`).
- **CẤM hardcode IP / URL nội bộ**: Quản lý qua file config môi trường hoặc tham số CLI (`argparse`).
- **CẤM hardcode số liệu không có căn cứ**: Toàn bộ số liệu báo cáo bắt buộc phải trích dẫn và truy vết từ transcript/glossary gốc.
- **QUY ĐỊNH FILE DUNG LƯỢNG LỚN (LOCAL ONLY)**: Các file lớn (file ghi âm audio, video, models, dumps) chỉ lưu trữ ở local, TUYỆT ĐỐI KHÔNG commit/push lên Git. Tự động loại trừ qua `.gitignore` và chốt chặn `tools/check_large_files.py` (tối đa **45 MB**).

## 3. NGUYÊN TẮC HARNESS ENGINEERING (ZERO HALLUCINATION & EVIDENCE-BASED)
- Tuân thủ chu trình 5 pha: `GATHER -> CURATE -> ACT -> VERIFY -> RETRY`.
- Mọi số liệu, tỷ lệ %, tiền tệ, deadline và quyết định của BOD phải gắn mã dẫn chứng `<span data-ref='file#HH:MM:SS'>` trỏ về dòng transcript gốc có thật.
- Biên bản họp trước khi xuất bản phải vượt qua **Cổng kiểm chứng tất định (Deterministic Gates)**:
  1. Độ phủ transcript: Mọi file trong `00_DANH_MUC_TRANSCRIPT.md` được sử dụng đầy đủ; họp Quý tách rõ từng bộ phận kèm khối `.bod-eval`.
  2. Dẫn chứng hợp lệ: 100% `data-ref` trỏ tới dòng có thật trong transcript.
  3. Khớp số liệu toán học: Mọi số liệu, %, tiền trong biên bản khớp chính xác với dòng transcript được trích dẫn.
  4. Phủ đủ chỉ đạo và giao việc của Ban Giám Đốc (`Chị Thanh (BOD)`).
  5. Chuẩn hoá danh xưng theo giới tính: `<Danh xưng Anh/Chị> <Tên> (<Tag Bộ phận>)` khớp danh bạ.
  6. Không chứa chuỗi cấm/sai lệch: `Bitrix`, `Natri`, `KIO`, `Kana`, `Rulico`, `Mr.`, `Ms.`, `Thư ký AI`.
  7. Bảng phân công đủ 4 cột; deadline hợp lệ (ngày làm việc trong tuần) hoặc ghi `Chưa xác định`.
  8. Chuẩn cấu trúc HTML/CSS (font Montserrat), cân bằng thẻ, lưu tại cổng xuất bản `output/` và ghi nhật ký chu trình vào `runs/<run_id>.jsonl`.

## 4. CHUẨN NGÔN NGỮ TIẾNG VIỆT & UNICODE
- 100% file mã nguồn, cấu hình, tài liệu dùng bảng mã **UTF-8** và chuẩn **Unicode dựng sẵn (NFC)**.
- Rà soát chính tả, kiểm soát lỗi đồng âm Whisper và chuẩn hoá danh xưng giới tính qua skill `vietnamese-spellcheck`.

## 5. QUẢN LÝ SKILL
- Mọi Skill bắt buộc lưu trữ, cập nhật tại `doc/Skill/<tên-skill>/` theo khai báo trong `.agents/skills.json` và đồng bộ đóng gói file `.skill` tương ứng.
