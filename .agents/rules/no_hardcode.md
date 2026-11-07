---
trigger: always_on
description: "Quy định bắt buộc tuyệt đối không hardcode đường dẫn, mật khẩu, token và thông tin cấu hình nhạy cảm"
---

# QUY ĐỊNH TUYỆT ĐỐI KHÔNG HARDCODE (ZERO HARDCODING POLICY)

1. **Không hardcode đường dẫn ổ đĩa tuyệt đối**:
   - Nghiêm cấm sử dụng các đường dẫn cứng như `C:\...`, `D:\...`, đường dẫn dự án cũ, `/home/...`.
   - Bắt buộc dùng `Path(__file__).resolve().parent.parent` hoặc biến môi trường `BASE_DIR`.

2. **Không hardcode thông tin bí mật / Thông tin xác thực**:
   - Nghiêm cấm ghi mật khẩu, PAT token (`ghp_...`, `github_pat_...`), API keys, Private keys vào mã nguồn.
   - Bắt buộc nạp từ biến môi trường `os.getenv(...)`, `.env` hoặc hệ thống quản lý credential an toàn.

3. **Không hardcode địa chỉ mạng và Host nội bộ**:
   - Dùng config hoặc tham số CLI (`argparse`).

4. **Không hardcode số liệu nghiệp vụ bịa đặt**:
   - Mọi số liệu trong biên bản họp phải truy vết được từ bằng chứng gốc (`citations` / `transcripts`).

5. **Quy định File dung lượng lớn (Chỉ lưu Local, cấm Push Git)**:
   - File âm thanh (.m4a, .mp3, .wav), video, AI model weights chỉ lưu ở local để xử lý, không bao giờ commit/push lên Git.
   - Luôn duy trì trong .gitignore và kiểm soát qua tools/check_large_files.py (ngưỡng tối đa 45 MB).
