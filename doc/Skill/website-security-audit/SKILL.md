---
name: "website-security-audit"
description: "Use when the user asks to scan, audit, or assess the security of a website (e.g. a company site) — runs passive recon and produces a severity-ranked vulnerability report."
---

# Website Security Audit (Passive Recon)

## Mục đích & giới hạn (đọc trước khi chạy)

Skill này thực hiện **trinh sát bảo mật thụ động (passive reconnaissance)** đối với một website — chỉ gửi các request GET tới các trang/endpoint công khai, giống như một khách truy cập bình thường hoặc search engine bot sẽ thấy. Mục tiêu là phát hiện thông tin bị lộ không chủ ý (misconfiguration, information disclosure) để báo cáo cho chủ sở hữu site khắc phục.

**Skill này KHÔNG được dùng để:**
- Chủ động khai thác lỗ hổng (SQLi, XSS payload thử nghiệm, path traversal thử nghiệm, RCE)
- Brute-force / thử đăng nhập, đoán mật khẩu
- Port scanning, DoS/DDoS, fuzzing
- Bất kỳ hành động nào có thể làm gián đoạn hoạt động của site hoặc vượt quá "đọc trang công khai"

Nếu người dùng muốn kiểm thử sâu hơn (khai thác thực tế, penetration test), hướng họ sang các công cụ chuyên dụng với sự cho phép rõ ràng của chủ sở hữu hạ tầng (xem mục "Công cụ bổ sung" bên dưới) — không tự thực hiện khai thác trong skill này dù được yêu cầu.

Trước khi chạy, xác nhận nhanh với người dùng (nếu chưa rõ) rằng đây là website họ có quyền đánh giá (site công ty họ, site họ quản trị) — không chạy recon nhắm vào bên thứ ba không liên quan mà không có lý do chính đáng.

## Quy trình thực hiện

Dùng `WebFetch` cho từng bước. Mỗi bước đều là GET tới một đường dẫn công khai — không cần đăng nhập, không cần thao tác với form.

### Bước 1 — Trang chủ & công nghệ nền tảng
Fetch trang chủ, yêu cầu model trích xuất: meta tags (generator, viewport, robots), script/link tags bên ngoài, comment trong HTML, form đăng nhập có lộ công khai không, footer/liên hệ có lộ thông tin nhạy cảm không.

→ Xác định: CMS (WordPress/Joomla/Drupal/custom), page builder, e-commerce plugin, SEO plugin, và version nếu lộ qua `meta-generator`.

### Bước 2 — REST API discovery (nếu là WordPress)
Fetch `{domain}/wp-json/` — đây là endpoint mặc định công khai của WordPress, liệt kê toàn bộ `namespaces` (= plugin đang active) và `routes`.

**Soi kỹ các route có khả năng nguy hiểm**, đặc biệt các namespace lạ (không phải core `wp/v2`, `wc/*`, `yoast/*`, `jetpack/*` quen thuộc). Cờ đỏ cần tìm trong tên route:
- `file/read`, `file/write`, `file/delete`, `file/edit` → đọc/ghi/xoá file trên server
- `cli/run`, `cli/execute`, `shell`, `exec`, `command` → chạy lệnh hệ thống
- `code-snippet`, `eval`, `php` → chèn/chạy code tuỳ ý
- `backup`, `export`, `import`, `migration`, `restore` → có thể lộ toàn bộ DB/source nếu không auth đúng
- `db`, `sql`, `query` → truy vấn database trực tiếp

Những route này thường đến từ các plugin "AI site builder" / "vibe coding" / migration / dev-tools — nếu thấy, đánh dấu **CRITICAL** và khuyến nghị kiểm tra cơ chế xác thực ngay, hoặc gỡ nếu không rõ mục đích.

### Bước 3 — User enumeration
Fetch `{domain}/wp-json/wp/v2/users` (WordPress) — endpoint này mặc định công khai và trả về danh sách user kèm `slug` (thường trùng username đăng nhập). Nếu trả về dữ liệu → đánh dấu **HIGH**, vì kẻ tấn công có username hợp lệ để brute-force.

### Bước 4 — XML-RPC
Fetch `{domain}/xmlrpc.php`. Nếu trả lỗi dạng "chỉ chấp nhận POST" (thay vì 404) → XML-RPC đang bật, đánh dấu **MEDIUM** (vector brute-force qua `system.multicall`, pingback amplification).

### Bước 5 — File/endpoint nhạy cảm thường bị lộ
Thử fetch (từng cái một, ghi nhận status/nội dung trả về, không thử đoán thêm biến thể nếu không có dấu hiệu):
- `/robots.txt`, `/sitemap.xml` — xem có path quản trị bị liệt kê không
- `/readme.html` (WordPress core) — lộ version chính xác
- `/.env`, `/wp-config.php.bak`, `/wp-config.php~`, `/.git/config` — file cấu hình/secret bị lộ do backup editor cẩu thả
- `/wp-content/debug.log` — log debug có thể chứa path, query, thông tin lỗi nhạy cảm

Nếu bất kỳ cái nào trả về nội dung thật (không phải 404) → đánh dấu mức độ theo nội dung lộ (file `.env`/`wp-config` lộ = **CRITICAL**, debug log = **MEDIUM**, version info = **LOW**).

### Bước 6 — Trang đăng nhập & cấu trúc truy cập công khai
Ghi nhận: `/wp-admin`, `/wp-login.php` có truy cập công khai không giới hạn IP không, có captcha/2FA dấu hiệu gì không, form đăng nhập có hiện ngay trên trang chủ không (tăng khả năng bị bot quét).

## Định dạng báo cáo đầu ra

Trình bày kết quả theo mức độ nghiêm trọng, giảm dần: **CRITICAL → HIGH → MEDIUM → LOW/INFO**. Mỗi phát hiện gồm:
1. Tên vấn đề
2. Bằng chứng cụ thể (endpoint, nội dung phản hồi tóm tắt)
3. Vì sao nguy hiểm (kịch bản khai thác khái quát — không viết payload/PoC chi tiết)
4. Khuyến nghị khắc phục cụ thể

Kết thúc báo cáo bằng mục "Giới hạn & bước tiếp theo": nhắc rõ đây là passive recon, không thay thế pentest thật, và gợi ý công cụ bổ sung bên dưới.

## Công cụ bổ sung (để giới thiệu cho người dùng, không tự chạy)

- **WPScan** — quét plugin/theme WordPress lỗi thời, đối chiếu CVE
- **securityheaders.com / Mozilla Observatory** — kiểm tra HTTP security headers (CSP, HSTS, X-Frame-Options...)
- **SSL Labs (ssllabs.com/ssltest)** — kiểm tra cấu hình TLS/chứng chỉ
- **OWASP ZAP / Burp Suite** — kiểm thử injection/XSS thực tế trên form (chỉ khi có uỷ quyền rõ ràng, chạy ngoài phạm vi skill này)
- Audit danh sách plugin active trong `wp-admin` đối chiếu CVE database — thường là việc rẻ và hiệu quả nhất nên làm trước

## Lưu ý về ngôn ngữ

Mặc định trả lời bằng tiếng Việt trừ khi người dùng yêu cầu khác, giữ văn phong kỹ thuật, chi tiết, phân tích rõ từng mục (theo phong cách người dùng đã quen).