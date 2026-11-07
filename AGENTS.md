# QUY TẮC CODEBASE & TIÊU CHUẨN NGÔN NGỮ: HỆ THỐNG CHUYỂN ĐỔI GHI ÂM (.M4A) THÀNH BIÊN BẢN HỌP TIẾNG VIỆT

Tài liệu này (`AGENTS.md`) thiết lập các quy tắc bắt buộc cho toàn bộ codebase trong workspace `d:\Source-Transcript`. Mọi tác vụ chỉnh sửa code, quản lý Skill, xử lý âm thanh, chuẩn hoá transcript và tạo biên bản họp (Meeting Note) đều phải tuân thủ nghiêm ngặt các nguyên tắc dưới đây.

---

## 0. Quy Tắc Quản Lý & Lưu Trữ Skill (`d:\Source-Transcript\doc\Skill\`)

1. **Thư mục gốc duy nhất cho mọi Skill trong dự án**:
   - Toàn bộ các Skill của dự án **bắt buộc** được lưu trữ, đọc và cập nhật trực tiếp tại thư mục: **`d:\Source-Transcript\doc\Skill\`** (đã được đăng ký tự động qua [`.agents/skills.json`](file:///d:/Source-Transcript/.agents/skills.json)).
   - **Khi tạo mới bất kỳ Skill nào**: Bắt buộc tạo thư mục con `d:\Source-Transcript\doc\Skill\<tên-skill>\SKILL.md` (kèm các thư mục `assets/`, `scripts/`, `resources/` nếu có). Tuyệt đối không tạo skill rải rác ở thư mục khác.
   - **Khi đọc và cập nhật Skill**: Luôn đọc từ `d:\Source-Transcript\doc\Skill\<tên-skill>\`, cập nhật trực tiếp vào thư mục đó, và đồng bộ đóng gói lại file nén `<tên-skill>.skill` (định dạng ZIP archive chứa thư mục `<tên-skill>/`) ngay trong `d:\Source-Transcript\doc\Skill\`.
2. **Các Skill chuẩn hiện có trong `d:\Source-Transcript\doc\Skill\`**:
   - [`ktt-transcript-normalizer`](file:///d:/Source-Transcript/doc/Skill/ktt-transcript-normalizer/SKILL.md): Nghe trực tiếp file ghi âm (`.m4a`), định danh chính xác nhân sự theo từng bộ phận/buổi họp và chuẩn hoá transcript, thuật ngữ hệ thống (`MISA AMIS`), thương hiệu & mã hàng của Công ty TNHH Kiên Thành Tín.
   - [`meeting-note`](file:///d:/Source-Transcript/doc/Skill/meeting-note/SKILL.md): Tạo và cập nhật biên bản họp HTML chuẩn in PDF A4 (gồm 3 khung [`khung_kickoff.html`](file:///d:/Source-Transcript/doc/Skill/meeting-note/assets/khung_kickoff.html), [`khung_weekly.html`](file:///d:/Source-Transcript/doc/Skill/meeting-note/assets/khung_weekly.html), [`khung_bsc_kpi.html`](file:///d:/Source-Transcript/doc/Skill/meeting-note/assets/khung_bsc_kpi.html) cho họp Báo cáo Quý / BSC & KPI từng bộ phận kèm đánh giá sau báo cáo của BOD, và [`style.css`](file:///d:/Source-Transcript/doc/Skill/meeting-note/assets/style.css) với letterhead & logo Công ty TNHH Kiên Thành Tín, font Montserrat).
   - [`vietnamese-spellcheck`](file:///d:/Source-Transcript/doc/Skill/vietnamese-spellcheck/SKILL.md): Kiểm tra và sửa lỗi chính tả, dấu thanh, khoảng trắng, danh xưng giới tính (`Anh`/`Chị`) và kiểm tra Unicode code point ([`check_unicode.py`](file:///d:/Source-Transcript/doc/Skill/vietnamese-spellcheck/scripts/check_unicode.py)).
   - [`mpp-project-reader`](file:///d:/Source-Transcript/doc/Skill/mpp-project-reader/SKILL.md): Đọc, phân tích tiến độ, WBS, critical path và chi phí từ file Microsoft Project (`.mpp`).

---

## 1. Quy tắc Chuẩn Chính Tả & Ngữ Pháp Tiếng Việt

1. **Chuẩn mã hoá & Unicode**:
   - Toàn bộ file mã nguồn (`.py`), cấu hình (`.txt`), tài liệu (`.md`, `.html`) và kết quả đầu ra bắt buộc dùng bảng mã **UTF-8** và chuẩn **Unicode dựng sẵn (NFC - Normalization Form C)**. Tuyệt đối không trộn lẫn ký tự Unicode tổ hợp (NFD) gây lỗi hiển thị dấu hoặc tìm kiếm.
   - Luôn tuân thủ quy trình rà soát của skill [`vietnamese-spellcheck`](file:///d:/Source-Transcript/doc/Skill/vietnamese-spellcheck/SKILL.md) trước khi bàn giao tài liệu.
2. **Chính tả Tiếng Việt chuẩn mực**:
   - Kiểm soát và sửa triệt để các lỗi phát âm vùng miền hoặc lỗi nhận dạng âm thanh đồng âm của AI:
     - Lỗi phụ âm đầu: `ch/tr`, `s/x`, `d/gi/r`, `l/n`, `v/d`.
     - Lỗi vần & phụ âm cuối: `c/t` (`iêc/iêt`, `ươc/ươt`, `ac/at`), `n/ng` (`an/ang`, `ên/êng`), `nh/n`, `ch/t`.
     - Lỗi dấu thanh: dấu hỏi (`?`) và dấu ngã (`~`).
   - Sửa các từ ghép Hán-Việt hay bị Whisper nhận sai trong ngữ cảnh công sở (ví dụ: *"phân tịch"* → *"phân tích"*, *"nghiệm thư"* → *"nghiệm thu"*, *"công lợ"* → *"công nợ"*, *"tiến đồ"* → *"tiến độ"*, *"đối xoát"* → *"đối soát"*).
3. **Thuật ngữ chuyên ngành & Tên riêng**:
   - Giữ đúng nguyên dạng viết hoa/viết thường của thuật ngữ kỹ thuật và quản trị (ví dụ: `MISA AMIS`, `CRM`, `ERP`, `BOD`, `KPI`, `OKR`, `SLA`, `UAT`, `go-live`, `master data`, `SQL Server`, `Power BI`).
   - Tự động đối chiếu và cập nhật vào [`doc/glossary.txt`](file:///d:/Source-Transcript/doc/glossary.txt).

---

## 2. Quy tắc Danh Xưng & Giới Tính (Gender) Chuẩn Tiếng Việt Công Sở

1. **Chuẩn hoá Danh xưng theo Giới tính (Gender Accuracy)**:
   - Trong biên bản họp tiếng Việt, danh xưng gắn liền với giới tính và vị thế giao tiếp (**Anh** cho Nam, **Chị** cho Nữ; hoặc **Ông / Bà** trong văn bản trang trọng với đối tác/HĐQT). Không dùng `Mr.` / `Ms.` nửa Anh nửa Việt trừ khi người dùng yêu cầu rõ.
   - **Bắt buộc viết hoa danh xưng khi đi kèm tên riêng**: `Anh Hùng`, `Chị Lan`, `Anh Tân (Kho)`, `Anh Khiêm (KT)`.
2. **Chống nhầm lẫn giới tính từ âm thanh (Anti-Misgendering)**:
   - Khi âm thanh `.m4a` nói nhanh hoặc nối âm, AI nhận dạng giọng nói rất dễ nghe nhầm *"anh"* thành *"em/chị"* hoặc ngược lại, hoặc dịch máy từ tiếng Anh (`he/she/they`, `Mr./Ms.`) sang từ thiếu tự nhiên (*"ông ấy/cô ấy/họ"*).
   - **Quy tắc bắt buộc**:
     - Luôn đối chiếu tên nhân sự với **Danh sách thành phần tham dự** (hoặc [`doc/glossary.txt`](file:///d:/Source-Transcript/doc/glossary.txt)) để áp đúng danh xưng `Anh` hoặc `Chị` xuyên suốt 100% văn bản.
     - Nếu một nhân sự được nhắc tên trong cuộc họp nhưng chưa rõ giới tính (`Anh` hay `Chị`), tuyệt đối **không tự đoán bừa giới tính** mà phải giữ nguyên tên kèm cờ `[cần xác nhận danh xưng: Anh/Chị <Tên>]` và liệt kê vào mục cần xác nhận cuối bài.
3. **Định dạng Tên + Tag bộ phận**:
   - Trong Biên bản họp (Meeting Note), mọi cá nhân khi được nhắc đến phải tuân theo định dạng: **`<Danh xưng Anh/Chị> <Tên> (<Tag Bộ phận>)`** (ví dụ: `Anh Tân (Kho)`, `Chị Mai (KT)`, `Anh Khiêm (KT)`), nhất quán 100% từ mục Thành phần tham dự đến Bảng phân công và Kết luận.
4. **Chuyển đổi đại từ khẩu ngữ sang văn phong biên bản**:
   - Lược bỏ và chuyển hoá các đại từ xưng hô khẩu ngữ/thân mật trong lời nói trực tiếp (*"mày - tao"*, *"tớ - cậu"*, *"nó"*, *"ông kia"*, *"bà đó"*) thành danh xưng lịch sự chuẩn mực (`Anh/Chị <Tên> (<Tag>)`, `bộ phận <Tag>`, `nhân sự phụ trách`).

---

## 3. Quy tắc Bảo Toàn Sự Thật (Zero Hallucination)

1. **Tuyệt đối không bịa đặt hoặc suy diễn**:
   - **KHÔNG** tự ý thêm ý kiến, **KHÔNG** tự suy đoán nguyên nhân, **KHÔNG** tự bịa ra **Số liệu, Tiền tệ, Tỷ lệ %, Ngày tháng, Deadline, hoặc Tên người phụ trách**.
   - Nếu thông tin về người thực hiện hoặc hạn hoàn thành (Deadline) không được chốt rõ trong cuộc họp, bắt buộc ghi **`Chưa xác định`** và tổng hợp vào danh sách cần bổ sung ở cuối biên bản.
2. **Quản lý đoạn âm thanh độ tin cậy thấp (`[??]`)**:
   - Mọi đoạn transcript có gắn thẻ `[??]` (do `avg_logprob` thấp hoặc `compression_ratio` cao) phải được trích xuất riêng kèm mốc thời gian `[HH:MM:SS -> HH:MM:SS]` để người duyệt kiểm tra lại.
   - Nếu đoạn `[??]` chứa con số, ngày tháng hoặc quyết định quan trọng, phải gắn nhãn `[cần kiểm tra - HH:MM:SS]` ngay tại vị trí đó trong biên bản.

---

## 4. Quy tắc Kỹ Thuật & Codebase (`transcribe_batch.py`)

1. **Xử lý âm thanh đầu vào (`.m4a`, `.mp3`, `.wav`...)**:
   - Dùng `ffmpeg` chuyển về WAV mono `16 kHz`, lọc tần số ngoài dải giọng nói (`highpass=f=80,lowpass=f=7600`) và cân bằng âm lượng động (`dynaudnorm`) để bắt rõ giọng người ngồi xa micro.
2. **Cấu hình `faster-whisper` tối ưu cho Tiếng Việt**:
   - Luôn ép `language="vi"`, bật `vad_filter=True` và `condition_on_previous_text=False` để ngăn chặn lỗi lặp câu vô tận.
   - Phải có bộ lọc `is_hallucination()` để loại bỏ các câu ảo giác tiếng Việt kinh điển của Whisper (như *"Hãy subscribe cho kênh..."*, *"Ghiền Mì Gõ"*, *"Cảm ơn các bạn đã theo dõi..."*).
3. **Xử lý Glossary (`doc/glossary.txt`)**:
   - Sắp xếp các cụm từ sửa lỗi (`sai => đúng`) theo thứ tự **từ dài đến ngắn** trước khi chạy Regex để cụm ngắn không cắt hỏng cụm dài.
   - Dùng ranh giới từ hỗ trợ đầy đủ ký tự tiếng Việt có dấu (`(?<![0-9A-Za-zÀ-ỹ_])...(?![0-9A-Za-zÀ-ỹ_])`) thay vì `\b` hay `\w` mặc định dễ lỗi khi từ chứa dấu gạch ngang hoặc ký tự đặc biệt.
   - Khi tạo `initial_prompt`, cắt theo ranh giới từ hoàn chỉnh, không cắt cụt giữa từ.
4. **Tương thích hệ điều hành Windows**:
   - Luôn cấu hình `sys.stdout.reconfigure(encoding="utf-8")` và ghi/đọc mọi file với `encoding="utf-8"`.
   - Đường dẫn mặc định của `glossary.txt` phải tự động tìm theo thư mục chứa script (`Path(__file__).resolve().parent / "glossary.txt"`) để chạy từ bất kỳ thư mục làm việc nào cũng không bị trượt glossary.
