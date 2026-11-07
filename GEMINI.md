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

## 3. NGUYÊN TẮC HARNESS ENGINEERING (ZERO HALLUCINATION)
- Tuân thủ chu trình 5 pha: `GATHER -> CURATE -> ACT -> VERIFY -> RETRY`.
- Biên bản họp trước khi xuất bản phải vượt qua **6 Cổng kiểm chứng tất định (6 Deterministic Gates)**:
  1. Khớp toán học & chú giải số liệu.
  2. Đồng bộ Section I (Tổng quan) và Section II (Chi tiết).
  3. Phủ đủ 100% chỉ đạo và giao việc của Ban Giám Đốc (`Chị Thanh (BOD)`).
  4. Chuẩn hoá danh xưng theo giới tính: `<Danh xưng Anh/Chị> <Tên> (<Tag Bộ phận>)`.
  5. Deadline hợp lệ (từ Thứ Hai đến Thứ Sáu, không rơi vào cuối tuần).
  6. Chuẩn cấu trúc biên bản 7 phần, cân bằng thẻ HTML.

## 3. CHUẨN NGÔN NGỮ TIẾNG VIỆT & UNICODE
- 100% file mã nguồn, cấu hình, tài liệu dùng bảng mã **UTF-8** và chuẩn **Unicode dựng sẵn (NFC)**.
- Rà soát chính tả, kiểm soát lỗi đồng âm Whisper và chuẩn hoá danh xưng giới tính qua skill `vietnamese-spellcheck`.

## 4. QUẢN LÝ SKILL
- Mọi Skill bắt buộc lưu trữ, cập nhật tại `doc/Skill/<tên-skill>/` theo khai báo trong `.agents/skills.json`.
