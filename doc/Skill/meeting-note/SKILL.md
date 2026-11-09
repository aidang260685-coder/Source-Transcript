---
name: meeting-note
description: >
  Tạo biên bản cuộc họp (meeting note) chuyên nghiệp dạng file HTML hoàn
  chỉnh, mở được trên trình duyệt và in ra PDF giữ nguyên màu sắc. Dùng
  skill này bất cứ khi nào người dùng muốn tạo biên bản họp, viết meeting
  note, tạo minutes of meeting, lập biên bản họp Báo cáo Quý / Đánh giá
  BSC & KPI của các bộ phận (có phần đánh giá sau báo cáo của BOD), chuyển
  nội dung cuộc họp (file ghi âm .m4a đã transcribe, note thô, thông báo
  họp + nội dung họp) thành file HTML, hoặc sửa/cập nhật một file meeting
  note HTML đã có (đổi tên người, đổi danh xưng giới tính Anh/Chị, đổi tên
  bộ phận, bổ sung nội dung, sửa deadline). Kích hoạt cả khi người dùng chỉ
  cung cấp nội dung thô của cuộc họp (danh sách người tham dự, báo cáo BSC/KPI
  từng phòng ban, nhận xét của BOD, vấn đề, deadline, quyết định) và yêu cầu
  tạo tài liệu, ngay cả khi không nói rõ từ "biên bản". Luôn dùng skill này
  khi đầu ra là một file HTML biên bản họp — không tự viết HTML từ đầu mà
  không đọc SKILL.md và các file trong assets/ trước, đồng thời phối hợp với
  quy tắc chính tả trong skill `vietnamese-spellcheck` và chuẩn nhân sự trong
  `ktt-transcript-normalizer`.
---

# Skill: Meeting Note (Biên Bản Họp)

Tạo file HTML biên bản họp chuẩn, chuyên nghiệp, đúng cấu trúc mẫu nhất
quán, chuẩn chính tả và danh xưng tiếng Việt (`Anh` / `Chị`), in PDF giữ màu,
có nút tải file. Skill này có **3 khung mẫu** khác nhau tùy loại cuộc họp
(`khung_kickoff.html`, `khung_weekly.html`, và `khung_bsc_kpi.html`) — bước
quan trọng nhất là **chọn đúng khung** trước khi viết nội dung.

---

## NGUYÊN TẮC BẢO MẬT & QUYỀN RIÊNG TƯ (STRICT PRIVACY)
- Mọi dữ liệu cuộc họp, báo cáo số liệu, thông tin cá nhân và tài khoản chia sẻ trong quá trình lập biên bản là thông tin bảo mật nội bộ.
- Tuyệt đối KHÔNG tự ý chia sẻ dữ liệu hoặc chuyển giao cho bất kỳ AI Agent nào khác nếu chưa có sự xác nhận (CONFIRM) trực tiếp từ người dùng.

---

## QUY TRÌNH XỬ LÝ

### Bước 1 — Thu thập thông tin

Trước khi tạo file, đảm bảo có đủ các thông tin sau (hỏi nếu thiếu, nhưng
nếu người dùng đã cung cấp nội dung thô/transcript thì tự trích xuất,
không hỏi lại những gì đã có):

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| Tiêu đề cuộc họp | ✅ | Ngắn gọn, mô tả chủ đề (ví dụ: Kickoff, Weekly, hoặc Báo cáo Quý BSC & KPI) |
| Ngày & giờ | ✅ | DD/MM/YYYY - HH:MM (hoặc ghi rõ các phiên Buổi 1 / Buổi 2 nếu họp nhiều buổi) |
| Thành phần tham dự | ✅ | Danh xưng (`Anh`/`Chị`) + Tên + **tag bộ phận viết tắt** (xem Bước 3) |
| Nội dung thảo luận / Báo cáo | ✅ | Vấn đề theo mục / Đánh giá theo team / Báo cáo BSC & KPI từng bộ phận |
| Đánh giá của BOD (với họp Quý) | Nếu là họp Quý | Nhận xét, chất vấn, định hướng và chỉ đạo của BOD ngay sau mỗi bộ phận báo cáo |
| Phân công / Action items | ✅ | Ai làm gì (`Anh/Chị Tên (Tag)`), deadline, đầu ra |
| Quyết định / Timeline | ✅ | Mốc thời gian, phương án, lộ trình rà soát |
| Rủi ro | Nếu có | Hậu quả cụ thể nếu không xử lý |
| Yêu cầu báo cáo | Nếu có | Ai báo cáo gì, lịch họp định kỳ / kênh liên lạc |
| Kết luận | ✅ | Điểm chốt, next steps |
| Tham chiếu | Nếu có | Cuộc họp trước, để liên kết mạch dự án / kỳ báo cáo trước |
| Người duyệt | ✅ | Danh xưng (`Anh`/`Chị`) + Tên người duyệt biên bản (ví dụ: `Chị Thanh (BOD)`) |

### Bước 2 — Chọn khung mẫu phù hợp

Đây là quyết định quan trọng nhất, vì nó định hình toàn bộ Section I, II và
III của biên bản:

1. **Họp Báo cáo Quý / Đánh giá BSC & KPI (Quarterly Review / BSC & KPI Review)** → đọc `assets/khung_bsc_kpi.html`:
   - **Dấu hiệu nhận diện**: Cuộc họp tổng kết Quý (Quý 1, 2, 3, 4) hoặc đánh giá thẻ điểm cân bằng **BSC (Balanced Scorecard)** và **KPI**; mỗi bộ phận/kênh (Kế toán, Mua hàng - PP, Kho, QC, Nhân sự - HR, IT, Marketing, Data - DA, Kinh doanh - Sale...) lần lượt trình bày kết quả BSC & KPI của bộ phận mình, kế hoạch quý tiếp theo, có thảo luận phản biện liên phòng ban và **phần đánh giá, nhận xét, chỉ đạo của BOD (`Chị Thanh (BOD)`) ngay sau báo cáo của từng bộ phận**.
2. **Có "Thông báo cuộc họp" (agenda) đánh số mục sẵn (Họp Weekly / Vận hành)** → đọc `assets/khung_weekly.html`:
   - **Dấu hiệu nhận diện**: Họp định kỳ hàng tuần/tháng sau go-live, đánh giá vận hành hệ thống với mục kiểu "I. Đánh giá của từng team sau X tuần triển khai" và "II. Nội dung cần giải quyết trong tuần: 1, 2, 3...".
3. **Không có agenda chia theo team, hoặc họp Kickoff / Triển khai dự án / Ad-hoc** → đọc `assets/khung_kickoff.html`:
   - **Dấu hiệu nhận diện**: Nội dung là một danh sách vấn đề rời rạc cần giải quyết hoặc triển khai dự án mới (không phải báo cáo BSC & KPI từng phòng ban).
4. **Không chắc** → hỏi người dùng 1 câu ngắn, hoặc nếu nội dung có nhắc tới chỉ tiêu KPI đạt/không đạt của các phòng ban và nhận xét của BOD thì ưu tiên chọn `khung_bsc_kpi.html`.

Đọc đúng file khung trước khi viết bất kỳ HTML nào — file đó có toàn bộ
comment giải thích khi nào dùng class CSS nào (`.open-issue` vs
`.highlight` vs `.tips-box` vs `.action-box` vs `.bod-eval`), và cấu trúc section theo
đúng thứ tự. Dán nguyên văn `assets/style.css` vào `<style>`.

### Bước 3 — Quy tắc map nội dung (áp dụng cho cả 3 khung)

**a) Map đúng cấu trúc theo loại khung:**
- **Với khung Weekly / Kickoff có agenda đánh số**: Section II của biên bản phải có **đủ và đúng thứ tự** từng mục trong "Thông báo cuộc họp" gốc — kể cả mục chỉ có 1 dòng. Không tự gộp hoặc đổi thứ tự.
- **Với khung Báo cáo Quý, BSC & KPI (`khung_bsc_kpi.html`)**:
  - **Tách riêng từng bộ phận / kênh báo cáo** thành các subsection độc lập (`1. Bộ phận Kế toán (KT)`, `2. Bộ phận Mua hàng & Kế hoạch (PP)`, `3. Bộ phận Kho`, `4. Bộ phận QC`, `5. Bộ phận Nhân sự (HR)`, `6. Bộ phận IT`, `7. Bộ phận Marketing (MKT)`, `8. Bộ phận Data (DA)`, `9. Khối Kinh doanh (Sale) - Kênh Đại lý / Nhà máy / Online & E-com / Michelin`...). Tuyệt đối không gộp chung báo cáo KPI của nhiều bộ phận vào một khối làm lu mờ trách nhiệm từng phòng ban.
  - **Cấu trúc bắt buộc bên trong MỖI bộ phận gồm 3 phần rõ ràng**:
    1. **Phần a — Kết quả thực hiện BSC & KPI và Kế hoạch Quý tới**: Trình bày bảng hoặc danh sách rõ ràng các chỉ số KPI thuộc 4 khía cạnh BSC (*Tài chính, Khách hàng, Quy trình nội bộ, Học hỏi & Phát triển*), gắn nhãn trạng thái `<span class="badge-pass">ĐẠT</span>`, `<span class="badge-fail">CHƯA ĐẠT</span>` hoặc `<span class="badge-warn">CẦN CẢI THIỆN</span>`, kèm số liệu thực tế (tỷ lệ %, doanh số, chi phí, tồn kho...), nguyên nhân và mục tiêu Quý tới. Nếu một bộ phận (ví dụ Sale) chỉ mới trình bày các chỉ số kinh doanh mà thiếu khía cạnh *Quy trình nội bộ* hoặc *Học hỏi & Phát triển* trên slide, ghi nhận đúng thực tế đã trình bày và nêu rõ điểm thiếu sót này ở phần thảo luận/đánh giá của BOD.
    2. **Phần b — Thảo luận & Phản biện liên bộ phận**: Ghi nhận đầy đủ các câu hỏi chất vấn, góp ý phối hợp giữa các phòng ban (ai hỏi, vướng mắc gì, người báo cáo giải trình ra sao, hai bên chốt hướng phối hợp thế nào).
    3. **Phần c — Đánh giá & Chỉ đạo của BOD sau báo cáo (`.bod-eval`)**: Đặt ngay dưới phần báo cáo & thảo luận của bộ phận đó trong hộp `<div class="bod-eval">`. Tóm tắt đầy đủ, sắc bén các nhận xét của BOD (`Chị Thanh (BOD)`): đánh giá tính hợp lý của KPI/mục tiêu (yêu cầu mục tiêu phải theo chuẩn **SMART**), chỉ ra nguyên nhân gốc rễ (như thiếu thiết kế hệ thống tổng thể, điều phối cảm tính, phân biệt QC với Checking & Testing, nguyên tắc Pareto 80/20...), và các yêu cầu hành động (Next Action) giao trực tiếp cho bộ phận đó.
  - **Tổng kết & Định hướng chiến lược của BOD (Section III)**: Tổng hợp các chỉ đạo cấp toàn công ty của BOD (như chuẩn hoá báo cáo đủ 4 khía cạnh BSC, lập dự án Thiết kế cấu trúc hệ thống vận hành & Hợp nhất sổ, rà soát dòng tiền liên bộ phận, cơ chế ngồi lại trong 7–10 ngày để ra giải pháp cho các thách thức liên phòng ban và review kết quả Done / Chưa Done ở kỳ sau).

**b) Chuẩn hoá Danh xưng Giới tính (Gender) & Tag bộ phận nhất quán cho mọi tên người.**
- Ngay từ phần thành phần tham dự, định nghĩa rõ **Danh xưng tiếng Việt (`Anh` cho Nam, `Chị` cho Nữ; hoặc `Ông`/`Bà` khi trang trọng)** và **Tag viết tắt cho mỗi bộ phận** (ví dụ `BOD`, `KT`, `PP`, `Kho`, `QC`, `HR`, `IT`, `MKT`, `DA`, `Sale`).
- **Chống dùng từ nửa Anh nửa Việt hoặc dịch máy**: Không dùng `Mr.` / `Ms.` trừ khi người dùng yêu cầu rõ; dùng chuẩn tiếng Việt **`Anh <Tên> (<Tag>)`** hoặc **`Chị <Tên> (<Tag>)`** (ví dụ: `Chị Thanh (BOD)`, `Anh Vũ (Kế toán)`, `Chị Linh Nhi (PP)`, `Anh Tân (Kho)`, `Anh Phương (QC)`, `Chị Ngọc (HR)`, `Anh Ân (IT)`, `Anh Duy (MKT)`, `Chị Vy (DA)`, `Anh Quang Tuẩn (Sale)`). Viết hoa chữ cái đầu của cả danh xưng `Anh`/`Chị` và Tên riêng.
- **Chống nhầm giới tính từ âm thanh `.m4a`**: Khi xử lý từ transcript âm thanh, AI nhận dạng giọng nói rất dễ nghe lướt chữ *"anh"* thành *"em/chị"* hoặc ngược lại. Bắt buộc đối chiếu với Danh sách thành phần tham dự, `ktt-transcript-normalizer` và `doc/glossary.txt` để giữ đúng 100% danh xưng `Anh`/`Chị` xuyên suốt toàn văn bản. Nếu có nhân sự mới chưa rõ giới tính, giữ nguyên tên kèm `[cần xác nhận danh xưng: Anh/Chị <Tên>]`.
- Từ phần Thành phần tham dự trở đi, MỌI lần nhắc tên người trong nội dung báo cáo, thảo luận, đánh giá của BOD, bảng phân công, lộ trình, kết luận đều phải đi kèm danh xưng + tag này — không nhắc tên trần trụi một mình.

**c) Vấn đề mở vs. đã có kết luận vs. đánh giá của BOD.**
- Dùng `.open-issue` (đỏ) cho vấn đề/rủi ro vẫn đang chờ xử lý hoặc theo dõi tiếp.
- Dùng `.highlight` (vàng) khi đã có kết luận cuối hoặc nhấn mạnh nguyên tắc vận hành/định hướng chiến lược toàn công ty.
- Dùng `.bod-eval` (cam đất nhạt) chuyên biệt cho khối **Đánh giá & Chỉ đạo của BOD ngay sau báo cáo của từng bộ phận** trong biên bản họp Quý BSC & KPI, giúp người đọc phân biệt ngay lập tức đâu là lời trình bày của phòng ban và đâu là nhận xét/chỉ đạo của Ban Giám đốc.

**d) Đánh giá hiệu suất (trễ deadline, thiếu báo cáo) đặt đúng vị trí ngữ nghĩa.**
- Với khung Weekly: đưa vào khối `.tips-box` "Đánh giá chung" ở đầu Section I.
- Với khung Kickoff: đưa vào một bullet trong phần liên quan ở Section II.
- Với khung Báo cáo Quý BSC & KPI: nếu một chỉ số hoặc dự án trong BSC bị trễ hạn (ví dụ dự án Mã truy xuất nguồn gốc trễ hạn tháng 4, hoặc bộ phận chưa cập nhật đủ 4 khía cạnh BSC), ghi rõ trạng thái `<span class="badge-fail">CHƯA ĐẠT / TRỄ HẠN</span>` ngay trong bảng BSC & KPI của bộ phận đó và nêu chỉ đạo chấn chỉnh trong khối `.bod-eval` tương ứng.

**e) Bảo toàn sự thật (Zero Hallucination) & Quản lý đoạn `[??]`.**
- Tuyệt đối không tự bịa hoặc suy đoán **số liệu, tiền tệ, tỷ lệ %, ngày tháng, deadline, tên người phụ trách**. Nếu chưa chốt trong cuộc họp, ghi rõ **`Chưa xác định`**.
- Nếu đầu vào có các đoạn gắn cờ `[??]` hoặc `[cần kiểm tra]` chứa số liệu/tên riêng mà người dùng chưa xác nhận lại, giữ nhãn `[cần kiểm tra - HH:MM:SS]` và liệt kê nhắc người dùng khi bàn giao.

### Bước 4 — Văn phong & Chuẩn Chính Tả Tiếng Việt

- Viết theo chuẩn **quản lý dự án & quản trị hiệu suất (BSC/KPI)**: rõ ràng, súc tích, có chủ thể hành động (`Anh/Chị <Tên> (<Tag>)`).
- Mỗi bullet point phải có **động từ hành động** (Hoàn thành, Kiểm tra, Phối hợp, Gửi, Đối soát, Nghiệm thu, Thiết kế, Chuẩn hoá...).
- Phân công phải ghi rõ **Anh/Chị Tên (tag bộ phận) + công việc cụ thể + deadline + bộ phận phối hợp/ghi chú** — không để mơ hồ.
- Rủi ro phải nêu **hậu quả** nếu không xử lý, không chỉ mô tả hiện trạng.
- Kết luận phải **chốt được** — không lặp lại nội dung đã nói ở các section trên.
- **Chuẩn chính tả Tiếng Việt** (phối hợp cùng skill `vietnamese-spellcheck`):
  - Đảm bảo mã hoá UTF-8 và chuẩn **Unicode dựng sẵn (NFC)**.
  - Kiểm tra kỹ lỗi dấu hỏi/ngã, phụ âm đầu (`tr/ch`, `s/x`, `d/gi/r`, `l/n`), vần cuối (`c/t`, `n/ng`) và từ Hán-Việt hay bị Whisper nhận sai (*phân tích, nghiệm thu, công nợ, đối soát, tiến độ, tồn kho...*).
  - Giữ đúng dạng chuẩn của thuật ngữ chuyên ngành và mã hàng (`MISA AMIS`, `AMIS CRM`, `AMIS Kế toán`, `App Kho`, `BSC`, `KPI`, `OKR`, `SLA`, `FIFO`, `UAT`, `go-live`, `master data`, `SQL Server`, `Power BI`, `n8n`, `NACHI`, `Koyo`, `ASAHI`, `Roleco`, `Cana`, `Michelin`, `NTN`).

### Bước 4b — Logo & Font công ty

**Logo KTT:**
```
https://assets.ktt.mthan.net/2026/06/cropped-Asset-6logo-avatar.png
```
Logo đã được nhúng sẵn trong cả 3 file khung. Hiển thị ngang hàng bên trái H1, cao 56px. `onerror="this.style.display='none'"` đảm bảo khi mất mạng/in offline, H1 tự căn giữa lại, không bể layout.

**Font chữ — Montserrat (Google Fonts):**

```css
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
```

- **Body text:** `Montserrat` weight 400 (Regular)
- **H1, H2, section title, table header:** `Montserrat` weight 700 (Bold)

Luôn dán `@import` này làm **dòng đầu tiên** trong `<style>` — trước tất cả khai báo CSS khác. Không dùng `font-weight: 800` hoặc `900` vì Montserrat chỉ tải 2 weight (400/700); trình duyệt sẽ tự fallback về 700.

**Quy đổi font size — Montserrat vs Times New Roman:**

Montserrat có x-height lớn hơn → trông to hơn cùng pt. Áp dụng bảng sau để giữ cảm giác kích thước tương đương khi in PDF:

| Thành phần | Times New Roman | Montserrat |
|---|---|---|
| Body / nội dung chính | 12pt | **10pt** |
| H1 (tiêu đề biên bản) | 22pt | **16pt** |
| H2 (chủ đề cuộc họp) | 16pt | **12pt** |
| Subsection title | 11pt | **9.5pt** |
| Company name (letterhead) | 12pt | **10pt** |
| Footer inline | 10pt | **8.5pt** |
| `line-height` | 1.6 | **1.5** |

**Spacing compact khi dùng Montserrat** (tránh kéo dài trang khi in):

```css
/* Callout boxes */
.highlight, .action-box, .open-issue, .tips-box, .bod-eval {
    padding: 8px 10px;
    margin: 8px 0;
}
.section-title  { padding: 7px 12px; margin: 14px 0 8px 0; }
.meta-info      { padding: 10px 13px; margin: 12px 0; }
table th, table td { padding: 7px 9px; }
p  { margin: 5px 0; }
ul { margin: 5px 0 5px 20px; }
li { margin: 3px 0; }
.footer { margin-top: 18px; padding-top: 10px; }
```

> **Mục tiêu:** Biên bản họp thông thường (Kickoff/Weekly) nên nằm trong **3–4 trang A4** khi in PDF. Riêng biên bản **Họp Báo cáo Quý (BSC & KPI)** có nhiều bộ phận báo cáo chi tiết có thể dài hơn theo số lượng phòng ban, nhưng vẫn áp dụng spacing compact để bố cục gọn gàng, chuyên nghiệp trên từng trang A4.

**Company letterhead — đặt TRÊN `<div class="header">`:**

```html
<div class="company-header">
  <span class="company-name">Công ty TNHH Kiên Thành Tín</span>
  <span class="company-address">66 An Dương Vương, P. An Lạc, Q. Bình Tân, TP. Hồ Chí Minh</span>
</div>
```

**Logo KTT — nằm ngang với H1 trong `<div class="header">`:**

```html
<div class="header">
  <div class="header-logo">
    <img src="https://assets.ktt.mthan.net/2026/06/cropped-Asset-6logo-avatar.png"
         alt="Kiên Thành Tín"
         onerror="this.style.display='none'">
    <h1 style="margin:0">BIÊN BẢN CUỘC HỌP</h1>
  </div>
  <h2>[Tên chủ đề]</h2>
</div>
```

**Số trang khi in PDF — tự động qua CSS Paged Media:**

```css
@page {
    @bottom-center {
        content: "Trang " counter(page) " / " counter(pages);
        font-family: 'Montserrat', sans-serif;
        font-size: 9pt;
        color: #7f8c8d;
    }
}
```

Hoạt động tốt trên Chrome/Edge. Trên màn hình hiển thị ghi chú tĩnh qua `.screen-page-label` (tự ẩn khi in). Thêm vào cuối `.footer`:

```html
<span class="screen-page-label">Số trang sẽ tự động hiển thị khi in PDF (Trang X / Y)</span>
```

### Bước 5 — Lưu file theo chuẩn Harness Engineering & Trình bày

Tuân thủ nghiêm ngặt cấu trúc phân tầng của **Harness Engineering**:
1. **Cổng xuất bản chính thức (Publishable Gate):** Bắt buộc lưu file HTML biên bản họp hoàn chỉnh (đã vượt qua kiểm định) tại thư mục **output/** theo định dạng Bien_Ban_Hop_[TieuDe]_[DD-MM-YYYY]_Verified.html (hoặc Bien_Ban_Hop_[TieuDe]_[DD-MM-YYYY].html), đồng bộ hàm downloadHTML() trong thẻ <script> cho khớp tên file.
2. **Dữ liệu chứng cứ & Quản lý transcript (Curated Evidence):** File bóc băng lời thoại .txt lưu tại **doc/transcripts/**, đồng thời cập nhật vào bảng kiểm **doc/transcripts/00_DANH_MUC_TRANSCRIPT.md**.
3. **Nhật ký chu trình (Run Traceability):** Ghi nhận trạng thái hoàn thành vào thư mục **
uns/** (.jsonl).
4. **Quy tắc Bảng phân công (Action Plan & Zero Hallucination):** Tuyệt đối KHÔNG tự suy đoán, gán ghép deadline hoặc công việc cụ thể nếu trong cuộc họp chưa thống nhất. Mọi đầu mục chưa chốt ngày phải ghi rõ Chưa xác định và nêu rõ điều kiện/thời điểm sẽ chốt.
5. **Báo cáo kết quả:** Kèm tóm tắt ngắn các mục chính và danh sách các điểm [??] / Chưa xác định cần người duyệt xác nhận — không re-summarize toàn bộ file.

---

## CALLOUT BOXES & BADGES — Dùng đúng loại

| Class | Màu | Dùng cho |
|---|---|---|
| `.highlight` | 🟡 Vàng | Quyết định/kết luận cuối, nguyên tắc vận hành, định hướng chiến lược tổng thể của BOD |
| `.action-box` | 🟢 Xanh lá | Kết luận cuộc họp, next steps, điểm chốt |
| `.open-issue` | 🔴 Đỏ nhạt | Vấn đề/rủi ro còn mở, chưa có kết luận xử lý |
| `.tips-box` | 🔵 Xanh nhạt | Lộ trình milestone, yêu cầu báo cáo, đánh giá chung/nhận định tổng quan |
| `.bod-eval` | 🟠 Cam nhạt | **Đánh giá, nhận xét & chỉ đạo trực tiếp của BOD** ngay sau phần báo cáo BSC & KPI của từng bộ phận |
| `.badge-pass` / `.badge-fail` / `.badge-warn` | 🟢/🔴/🟡 Nhãn | Nhãn trạng thái chỉ tiêu BSC & KPI (`ĐẠT` / `CHƯA ĐẠT` / `CẦN CẢI THIỆN`) trong bảng báo cáo bộ phận |

---

## XỬ LÝ CÁC TRƯỜNG HỢP ĐẶC BIỆT

### Họp Báo cáo Quý (BSC & KPI) kéo dài nhiều buổi hoặc tách nhiều file ghi âm theo bộ phận
Khi người dùng cung cấp nhiều file ghi âm/transcript của một kỳ họp Báo cáo Quý (ví dụ: mỗi bộ phận `Kế toán`, `PP`, `Kho`, `QC`, `HR`, `IT`, `Marketing`, `DA`, `Sale - Đại lý / Nhà máy / Online / Michelin` là 1–2 file riêng, kèm các file nhận xét/tổng kết của `Chị Thanh (BOD)`):
1. Nếu người dùng yêu cầu lập **Biên bản tổng hợp toàn kỳ họp Quý**: Gộp tất cả các bộ phận vào một file HTML duy nhất theo `assets/khung_bsc_kpi.html`, sắp xếp các bộ phận theo trình tự hợp lý (hoặc theo thứ tự phiên họp Buổi 1 / Buổi 2), gắn đúng các đoạn nhận xét rời của BOD (như nhận xét kênh Nhà máy, nhận xét sau trình bày team Sales, chia sẻ cùng Marketing, tổng kết cuối buổi) vào đúng khối `.bod-eval` của bộ phận đó và Section III (Đánh giá tổng thể của BOD).
2. Nếu người dùng yêu cầu lập **Biên bản báo cáo BSC & KPI cho riêng 1 bộ phận/khối**: Vẫn dùng `assets/khung_bsc_kpi.html` nhưng tập trung chi tiết vào các chỉ số BSC/KPI, thảo luận liên phòng ban và đánh giá của BOD dành riêng cho bộ phận/khối đó.

### Sửa file HTML đã có — quét toàn file trước khi sửa

Khi người dùng yêu cầu đổi tên người/danh xưng (`Anh`/`Chị`)/bộ phận, chuyển bộ phận của một
người, hoặc sửa một chi tiết xuất hiện nhiều lần (rất phổ biến vì tag bộ
phận theo Bước 3b lặp lại ở nhiều section):

1. Đọc file HTML hiện tại.
2. Tìm kiếm tất cả các dòng có liên quan đến tên/từ khóa cần đổi trước khi sửa — đừng chỉ sửa chỗ đầu tiên tìm thấy.
   Một cái tên thường xuất hiện ở: meta-info, subsection title, đoạn mô
   tả, bảng BSC/KPI, khối `.bod-eval`, bảng phân công, lộ trình, và kết luận — bỏ sót một chỗ sẽ làm file
   mâu thuẫn nội bộ (ví dụ vẫn còn 1 dòng ghi sai danh xưng hoặc bộ phận của người đó).
3. Thay thế đầy đủ ở tất cả vị trí rồi kiểm tra lại xem còn sót không.

### Bổ sung nội dung mới vào file đã có

Xác định đúng section ngữ nghĩa theo Bước 3a/3d và bảng callout box ở trên
trước khi chèn — đừng mặc định thêm vào cuối file hoặc tạo section mới
nếu nội dung đó thuộc về một section hoặc một bộ phận đã tồn tại.

### Chuyển đổi format cũ sang mẫu chuẩn

Nếu file HTML có cấu trúc khác (font khác, màu khác, class khác): giữ
nguyên 100% nội dung, thay toàn bộ CSS/cấu trúc theo `assets/style.css`
và khung tương ứng, tạo file mới (không ghi đè file gốc).

### Nội dung thô (raw text / transcript `.m4a`)

Tự phân tích cấu trúc: bộ phận nào báo cáo chỉ số BSC/KPI gì, đạt hay chưa đạt, ai chất vấn gì, BOD đánh giá và chỉ đạo gì, ai làm gì — rồi map vào
đúng section theo khung đã chọn ở Bước 2. Chuẩn hoá chính tả tiếng Việt,
danh xưng `Anh`/`Chị` theo giới tính và văn phong quản lý dự án nếu nguyên
bản còn thô, nhưng không bịa thêm số liệu/deadline không có trong nguồn.

---

## KIỂM TRA TRƯỚC KHI XUẤT FILE

- [ ] Đã chọn đúng khung (`kickoff` vs `weekly` vs `bsc_kpi`) theo Bước 2
- [ ] Nếu là họp Báo cáo Quý (`khung_bsc_kpi.html`): mỗi bộ phận có mục báo cáo BSC & KPI riêng + thảo luận liên bộ phận + khối `.bod-eval` đánh giá của BOD ngay phía dưới
- [ ] `@import Montserrat` là dòng đầu tiên trong `<style>`
- [ ] `font-family: 'Montserrat', sans-serif` trên body, h1, h2; font-weight dùng 400/700
- [ ] `.company-header` có tên công ty + địa chỉ, đặt TRÊN `<div class="header">`
- [ ] Header có `.header-logo` với logo KTT (URL: assets.ktt.mthan.net) và `onerror` fallback
- [ ] `@page @bottom-center` có `content: "Trang " counter(page) " / " counter(pages)`
- [ ] `.screen-page-label` nằm trong `.footer` sau dòng người duyệt
- [ ] H1 in hoa, font-weight 700, màu đen
- [ ] Tất cả section dùng đúng class `.section-title`, đánh số La Mã liên tục
- [ ] Section II khớp đúng số thứ tự agenda gốc (nếu có agenda) hoặc tách rõ từng bộ phận báo cáo (nếu là họp Quý BSC & KPI)
- [ ] **Mọi tên người đều có danh xưng đúng giới tính (`Anh`/`Chị`) + tag bộ phận đi kèm**, nhất quán 100% với phần thành phần tham dự
- [ ] **Đã rà soát chính tả tiếng Việt** theo `vietnamese-spellcheck` (Unicode NFC, dấu hỏi/ngã, phụ âm đầu, khoảng trắng dấu câu)
- [ ] Bảng phân công có đủ 4 cột: Người thực hiện/phụ trách, Công việc, Deadline, Ghi chú/Bộ phận phối hợp
- [ ] Callout boxes & badges dùng đúng loại (`.highlight`, `.action-box`, `.open-issue`, `.tips-box`, `.bod-eval`, `.badge-pass`, `.badge-fail`, `.badge-warn`)
- [ ] `print-color-adjust: exact` có mặt trong CSS
- [ ] `@media print` có `!important` cho tất cả background (kể cả `.bod-eval` và `.badge-*`)
- [ ] Nút tải file có hàm `downloadHTML()` với tên file đã sửa đúng (không còn placeholder)
- [ ] Footer có ngày lập và thông tin nhân sự chuẩn: `Thư ký / Người ghi chép & tổng hợp: [Anh/Chị Tên (Tag)] — Chủ trì & Phê duyệt: [Anh/Chị Tên (BOD)]`. Tuyệt đối KHÔNG ghi "Thư ký AI" hay "AI Meeting note", không ghi tên thiếu danh xưng giới tính.
- [ ] Font size và Line-height chuẩn văn bản hành chính công sở (body 10.5pt, line-height 1.7; bảng biểu 9.5pt, line-height 1.65)
- [ ] H1 in hoa font-weight 700 (không dùng font-weight 800/900 vì Montserrat đã rất đậm ở 700)
