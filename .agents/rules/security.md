---
trigger: always_on
description: "Quy tắc bảo mật thông tin người dùng, bí mật đăng nhập và ngăn ngừa rò rỉ dữ liệu qua các Agent"
---

# NGUYÊN TẮC BẢO MẬT & BẢO VỆ DỮ LIỆU NGƯỜI DÙNG (STRICT PRIVACY POLICY)

1. **Bảo mật thông tin người dùng chia sẻ**:
   - Mọi thông tin nhạy cảm (bao gồm: mật khẩu, tài khoản, Personal Access Token, API Key, thông tin cá nhân, email, tài liệu nội bộ, file âm thanh họp) CHỈ được sử dụng nội bộ để thực hiện tác vụ được người dùng trực tiếp yêu cầu.

2. **CẤM TỰ Ý CHIA SẺ VỚI AGENT AI KHÁC**:
   - Tuyệt đối KHÔNG tự ý chia sẻ, truyền tải, chuyển tiếp qua tin nhắn/prompt hay log cho bất kỳ AI Agent, Sub-agent, hệ thống bên ngoài hoặc bên thứ ba nào.

3. **BẮT BUỘC CONFIRM TỪ NGƯỜI DÙNG**:
   - Nếu một tác vụ kỹ thuật cần ủy quyền hoặc sử dụng lại mật khẩu / token cho bất kỳ bên nào khác, AI Agent BẮT BUỘC PHẢI HỎI RÕ VÀ ĐƯỢC NGƯỜI DÙNG XÁC NHẬN (CONFIRM) trước khi thực hiện.

4. **Bảo vệ mã nguồn & Nhật ký (Log Sanitization)**:
   - Tuyệt đối không ghi mật khẩu hay mã bí mật vào file mã nguồn, file log, git commit hoặc git config.
