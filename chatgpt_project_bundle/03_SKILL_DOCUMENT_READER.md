# HƯỚNG DẪN ĐỌC & BÓC TÁCH TÀI LIỆU PDF VÀ HTML (DOCUMENT READER SKILL)

Tài liệu này cung cấp phương pháp tiếp nhận, phân tích và trích xuất dữ liệu từ các file PDF và file mã nguồn HTML mà không làm mất cấu trúc bảng biểu, không làm biến dạng số liệu và không gây quá tải cửa sổ ngữ cảnh.

---

## 1. QUY TRÌNH TIẾP NHẬN & XỬ LÝ FILE HTML

Khi người dùng cung cấp file HTML hoặc nội dung mã nguồn HTML:
1. **Lọc sạch mã rác (Noise Stripping)**:
   - Tự động bỏ qua các khối thẻ không mang thông tin ngữ nghĩa: `<style>`, `<script>`, `<svg>`, `<noscript>`, `<iframe>`.
   - Giữ lại toàn bộ nội dung văn bản trong các thẻ ngữ nghĩa: `<title>`, `<h1>` - `<h6>`, `<p>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<blockquote>`, `<div class="...">`.
2. **Bảo toàn cấu trúc Bảng (`<table>`)**:
   - Chuyển đổi toàn bộ `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>` thành bảng định dạng Markdown chuẩn.
   - Giữ nguyên các thông tin chỉ số, đơn vị tính, tỷ lệ % và trạng thái ghi trong các ô bảng.
3. **Nhận diện các khối dữ liệu đặc thù**:
   - Khối nhận xét lãnh đạo (`class="bod-eval"`): Đánh dấu rõ đây là nhận xét/chỉ đạo của Ban Giám Đốc.
   - Khối vấn đề mở (`class="open-issue"`): Đánh dấu đây là rủi ro hoặc việc còn tồn đọng cần theo dõi.
   - Thẻ huy hiệu trạng thái (`class="badge-pass"`, `"badge-fail"`): Chuyển thành text `[ĐẠT]`, `[CHƯA ĐẠT]`.
4. **Kiểm tra tính toàn vẹn**:
   - Đảm bảo trích xuất đủ tất cả các phần từ Section I đến Section VII, không cắt cụt giữa chừng.

---

## 2. QUY TRÌNH TIẾP NHẬN & XỬ LÝ FILE PDF

Khi người dùng tải lên file tài liệu PDF:
1. **Xử lý luồng đọc đa cột (Multi-column Flow)**:
   - Nhận diện các văn bản trình bày theo 2 hoặc 3 cột. Đọc hết nội dung từ trên xuống dưới của cột bên trái trước khi chuyển sang cột bên phải. Tuyệt đối không đọc quét ngang làm trộn lẫn câu từ giữa hai cột.
2. **Khôi phục Bảng biểu trong PDF**:
   - Nếu trong PDF có bảng biểu được kẻ ô hoặc căn chỉnh theo tab, hãy tái tạo lại thành bảng Markdown có đầy đủ hàng và cột tương ứng.
   - Đối soát số liệu cột tổng (Total) với tổng các hàng con để tránh hiện tượng AI nhận dạng thiếu dòng.
3. **Phân biệt Header / Footer / Số trang**:
   - Loại bỏ các dòng lặp lại như tiêu đề đầu trang (Running header), chân trang (Running footer) để tránh làm loãng nội dung cốt lõi.
   - Ghi nhận số trang của thông tin quan trọng để tiện trích dẫn nguồn khi cần.
4. **Nhận diện bảng mã và lỗi font**:
   - Đảm bảo văn bản trích xuất sử dụng chuẩn Unicode dựng sẵn (NFC). Nếu phát hiện lỗi gõ dấu hoặc ký tự lạ do font PDF lỗi, tự động hiệu chỉnh về từ tiếng Việt chuẩn nghĩa.

---

## 3. TIÊU CHUẨN ĐẦU RA KHI PHÂN TÍCH TÀI LIỆU
Khi được yêu cầu tóm tắt hoặc bóc tách dữ liệu từ PDF/HTML, câu trả lời phải có cấu trúc:
1. **Thông tin hồ sơ tài liệu**: Tên tài liệu, Tổ chức ban hành, Ngày ban hành, Phiên bản, Người lập/duyệt.
2. **Tóm tắt điều hành (Executive Summary)**: 3–5 điểm trọng yếu nhất của tài liệu.
3. **Bảng số liệu cốt lõi**: Trích xuất các chỉ tiêu định lượng, doanh thu, chi phí, tồn kho, KPI.
4. **Danh mục hành động / Chỉ đạo**: Ai làm gì, thời hạn nào, kết quả đầu ra là gì.
5. **Ghi chú cảnh báo bất thường**: Chỉ ra các mâu thuẫn số liệu nội bộ (nếu có) để người dùng lưu ý.
