---
name: vietnamese-spellcheck
description: Kiểm tra và sửa lỗi chính tả, dấu câu, khoảng trắng, và danh xưng giới tính (Anh/Chị) tiếng Việt trong tài liệu (Transcript cuộc họp, Word, HTML, Excel, văn bản thường), và phòng ngừa lỗi mất dấu do FONT khi tạo/xuất file .docx/.html. Dùng khi người dùng yêu cầu "kiểm tra chính tả", "soát lỗi", "rà lại tiếng Việt", "proofread tiếng Việt", "chuẩn hoá transcript", hoặc khi vừa tạo/chỉnh sửa xong tài liệu tiếng Việt (như biên bản họp meeting note) cần rà trước khi giao. Kích hoạt cả khi chỉ nói "update tài liệu"/"chỉnh lại văn bản" kèm yêu cầu chính tả và giới tính (Gender). Cũng dùng khi người dùng báo "chữ này sai/thiếu dấu" qua ảnh chụp, bản xem trước, hoặc sau khi mở file .docx thật — có quy trình kiểm tra Unicode (script `check_unicode.py`) để phân biệt lỗi chính tả thật với lỗi hiển thị do font (§7), và quy trình bắt buộc kiểm tra/đổi font an toàn (§8). Gồm danh mục lỗi thường gặp (dấu hỏi/ngã, ch/tr, s/x, l/n, d/gi/r, thiếu dấu, sai khoảng trắng, lặp từ, nhầm danh xưng giới tính Anh/Chị từ âm thanh) và quy trình rà soát trước khi xuất bản.
---

# Kiểm tra chính tả & Chuẩn hoá Danh xưng Tiếng Việt

Skill này dùng để rà soát lỗi chính tả, ngữ pháp cơ bản, danh xưng giới tính (`Anh`/`Chị`) và trình bày trong văn bản tiếng Việt trước khi bàn giao cho người dùng (transcript cuộc họp `.m4a`, biên bản họp HTML, tài liệu Word, Excel, email, v.v.).

> **BẢO MẬT & QUYỀN RIÊNG TƯ (STRICT PRIVACY)**: Văn bản, dữ liệu nội bộ và thông tin người dùng chia sẻ chỉ phục vụ việc rà soát chính tả. Tuyệt đối KHÔNG tự ý chia sẻ dữ liệu hoặc thông tin tài khoản/mật khẩu cho bất kỳ AI Agent nào khác nếu chưa có sự xác nhận (CONFIRM) từ người dùng.

## Quy trình rà soát

1. **Lấy toàn bộ văn bản gốc** — nếu là file (.docx, .html, .xlsx, .txt), trích xuất text thuần trước (dùng `pandoc -t markdown file.docx` cho Word, hoặc đọc trực tiếp với HTML/Markdown/TXT).
2. **Quét theo từng danh mục lỗi** ở phần "Danh mục lỗi thường gặp" bên dưới — đọc kỹ từng câu, không chỉ dựa vào cảm giác quen mắt.
3. **Kiểm tra ở mức Unicode cho các chữ bị nghi ngờ** (xem mục 7 bên dưới) — đặc biệt khi người dùng báo "chữ này sai" nhưng mắt đọc thấy bình thường. Đừng chỉ tin vào bản xem trước (preview) trong giao diện chat; xác minh bằng code point trước khi kết luận file sai hay đúng. Dùng script có sẵn: `python scripts/check_unicode.py <file.docx> "cụm từ nghi vấn"` (hoặc `--scan` để quét toàn bộ các chữ có dấu chồng trong file).
4. **Lập danh sách lỗi phát hiện được**, mỗi lỗi gồm: vị trí (câu/đoạn), từ sai → từ đúng, lý do ngắn gọn.
5. **Trình bày danh sách lỗi cho người dùng trước khi sửa hàng loạt**, trừ khi người dùng đã yêu cầu rõ "sửa luôn giúp tôi" hoặc đang trong quy trình chuẩn hoá transcript tự động — khi đó có thể sửa trực tiếp rồi báo cáo tóm tắt các thay đổi.
6. **Áp dụng sửa lỗi vào file gốc** bằng công cụ phù hợp với định dạng file (docx: `str_replace` trên `word/document.xml` sau khi unzip, hoặc viết lại bằng docx-js nếu file được tạo từ script; xlsx: chỉnh trực tiếp ô; HTML/TXT: sửa trực tiếp).
7. **Không tự ý đổi văn phong hay nội dung kỹ thuật** (tên lệnh, đường dẫn, mã, số liệu, deadline, tên riêng, thuật ngữ tiếng Anh giữ nguyên) — skill này chỉ sửa lỗi chính tả/dấu câu/khoảng trắng/danh xưng chuẩn, không viết lại câu làm đổi nghĩa trừ khi câu đó sai ngữ pháp rõ ràng.

## Danh mục lỗi thường gặp

### 1. Dấu thanh (dấu hỏi ~ dấu ngã) & Từ ghép Hán-Việt trong công sở
Cặp từ dễ nhầm — kiểm tra theo nghĩa trong câu, không đoán theo thói quen vùng miền:
- **sử** (sử dụng) vs **sữa** (sữa uống) — khác nghĩa hoàn toàn, dễ gõ nhầm khi gõ nhanh.
- **giữ** (giữ lại) vs **giử** (sai chính tả, không tồn tại).
- **đã** vs **đả**, **sẽ** vs **sẻ**, **vẫn** vs **vẩn**, **những** vs **nhửng** (sai).
- Từ Hán-Việt hay sai dấu hoặc bị Whisper nhận nhầm từ âm thanh:
  - **hoàn thành** (không phải "hòan thành").
  - **phân tích** (hay bị nhận nhầm thành "phân tịch").
  - **nghiệm thu** (hay bị nhận nhầm thành "nghiệm thư").
  - **công nợ** (hay bị nhận nhầm thành "công lợ").
  - **đối soát** (hay bị nhận nhầm thành "đối xoát").
  - **tiến độ** (hay bị nhận nhầm thành "tiến đồ").
  - **quản lý/quản lí**, **kỹ thuật/kĩ thuật** (cả hai đều dùng được, nhưng phải nhất quán một kiểu trong toàn tài liệu).

### 2. Phụ âm đầu & Phụ âm cuối dễ lẫn
- **tr/ch**: trải nghiệm (không phải "chải nghiệm"), triển khai (không phải "chiển khai"), chương trình (không phải "trương trình").
- **s/x**: sử dụng (không phải "xử dụng" — lỗi rất phổ biến!), sắp xếp, kiểm soát (không phải "kiểm xoát"), rà soát (không phải "rà xoát"), đề xuất (không phải "đề suất"), sản xuất (không phải "sản suất"), xác nhận (không phải "sác nhận").
- **d/gi/r**: giữ (không phải "dữ" khi ý là "giữ lại"), bàn giao (không phải "bàn dao"), giải quyết (không phải "dải quyết").
- **l/n**: kiểm tra kỹ nếu văn bản từ bản ghi âm có người nói ngọng `l/n` (ví dụ: "lội dung" → "nội dung", "nàm việc" → "làm việc").
- **c/t & n/ng**: kiểm tra các vần dễ bị nhận sai từ giọng miền Nam/Trung trong file ghi âm `.m4a` (ví dụ: "chi tiếc" → "chi tiết", "công việt" → "công việc", "báo cáo" vs "báo cấu", "khách hàn" → "khách hàng").

### 3. Chuẩn hoá Danh xưng & Giới tính (Gender) trong Tiếng Việt
Đây là yêu cầu bắt buộc đối với biên bản họp và tài liệu doanh nghiệp Việt Nam:
- **Đúng giới tính (`Anh` cho Nam, `Chị` cho Nữ, `Ông`/`Bà` khi trang trọng)**:
  - Luôn đối chiếu tên nhân sự với **Danh sách thành phần tham dự** hoặc [`doc/glossary.txt`](file:///d:/Source-Transcript/doc/glossary.txt).
  - Trong file ghi âm `.m4a`, người nói nhanh thường nối âm khiến AI nhận nhầm *"anh"* thành *"em/chị"* hoặc ngược lại (ví dụ: *"chị Minh"* trong khi Minh là Nam trong danh sách tham dự → phải sửa thành **`Anh Minh`**).
- **Quy tắc viết hoa danh xưng đi kèm tên riêng**:
  - Khi danh xưng đứng trước tên riêng, viết hoa cả Danh xưng lẫn Tên: **`Anh Hùng`**, **`Chị Lan`**, **`Anh Tân (Kho)`**, **`Chị Mai (KT)`**.
- **Không dùng từ dịch máy hoặc khẩu ngữ suồng sã**:
  - Sửa các cụm dịch máy thiếu tự nhiên (*"anh ấy/cô ấy/ông ta/bà ta/họ"*) hoặc đại từ khẩu ngữ trong lời nói trực tiếp (*"mày/tao"*, *"nó"*, *"ông kia/bà đó"*) thành danh xưng công sở lịch sự: **`Anh/Chị <Tên> (<Bộ phận>)`**.
  - Nếu gặp một tên riêng chưa rõ giới tính và không có trong danh sách tham dự, không tự đoán mò mà gắn cờ **`[cần xác nhận danh xưng: Anh/Chị <Tên>]`**.

### 4. Thiếu hoặc sai dấu (dễ xảy ra khi gõ Telex nhanh)
- Thiếu dấu mũ/dấu móc: "thanh toan" thiếu dấu → "thanh toán"; "chuyen" → "chuyển".
- Gõ nhầm dấu do gõ Telex: "sẻ" gõ thành "sẽ" khi bấm nhầm phím x/j.
- Từ viết tắt/tên riêng bị bỏ dấu không nhất quán (ví dụ "Cai dat" thay vì "Cài đặt").

### 5. Khoảng trắng và dấu câu
- Dấu câu (`,` `.` `:` `;` `?` `!`) phải sát vào từ trước, có một khoảng trắng sau — không có khoảng trắng trước dấu câu.
- Không để hai khoảng trắng liên tiếp.
- Ngoặc kép/ngoặc đơn tiếng Việt: dùng nhất quán trong cùng tài liệu, không có khoảng trắng thừa bên trong sát dấu ngoặc.
- Số và đơn vị: khoảng trắng giữa số và đơn vị (ví dụ "16 ký tự", "30 ngày" — không viết dính "16ký tự", "30ngày").

### 6. Nhất quán thuật ngữ trong toàn tài liệu
- Giữ đúng nguyên dạng viết hoa/thường của các thuật ngữ chuyên ngành và hệ thống: `MISA AMIS`, `AMIS`, `CRM`, `ERP`, `BOD`, `KPI`, `OKR`, `SLA`, `UAT`, `go-live`, `master data`, `SQL Server`, `Power BI`.
- Một thuật ngữ hoặc Tag bộ phận chỉ nên dùng theo MỘT cách xuyên suốt (ví dụ: đã chọn `Anh Tân (Kho)` thì dùng lại đúng cụm này ở mọi chỗ).

### 7. Kiểm tra Unicode — phân biệt lỗi thật với lỗi hiển thị (font rendering)
Khi người dùng báo "chữ này sai" (đặc biệt là báo qua ảnh chụp màn hình bản xem trước/preview trong ứng dụng), **đừng vội sửa hoặc vội xin lỗi** — trước tiên xác minh xem lỗi nằm trong dữ liệu file hay chỉ là cách trình xem hiển thị:

1. Đảm bảo toàn bộ văn bản được chuẩn hoá về **Unicode dựng sẵn (NFC - Normalization Form C)** bằng `unicodedata.normalize("NFC", text)`. Không để lọt ký tự Unicode tổ hợp (NFD) gây lỗi tìm kiếm và lỗi nhảy dấu.
2. Trích xuất đúng đoạn text nghi vấn ra từ file gốc (không phải từ ảnh chụp), rồi kiểm tra từng ký tự bằng Python (`scripts/check_unicode.py`):
   ```python
   import zipfile, re, unicodedata
   with zipfile.ZipFile('file.docx') as z:
       data = z.read('word/document.xml').decode('utf-8')
   texts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', data)
   full = ''.join(texts)
   idx = full.find('CỤM TỪ NGHI VẤN')
   for ch in full[idx:idx+20]:
       print(hex(ord(ch)), unicodedata.name(ch, '?'))
   ```
3. So khớp với bảng ký tự tiếng Việt có dấu chồng (2 dấu trên 1 nguyên âm) — đây là nhóm dễ bị trình xem render sai nhất vì dấu mũ/móc chồng lên dấu thanh:
   - `ệ` U+1EC7 (E circumflex + dot below), `ẫ` U+1EAB (A circumflex + tilde), `ỡ` U+1EE1 (O horn + tilde), `ữ` U+1EEF (U horn + tilde), `ặ` U+1EB7 (A breve + dot below), `ộ` U+1ED9 (O circumflex + dot below) — và các chữ HOA tương ứng (Ệ U+1EC6, Ẫ U+1EAA, Ỡ U+1EE0, Ữ U+1EEE...).
   - Nếu code point đúng như bảng trên → **văn bản trong file là đúng chính tả**, dù ảnh chụp trông có vẻ sai.

### 8. Phòng ngừa lỗi mất dấu do FONT — kiểm tra trước khi giao file
Đây là nguyên nhân phổ biến nhất gây "mất dấu" mà dữ liệu Unicode vẫn hoàn toàn đúng:
- **Font rủi ro cao, tránh dùng làm font mặc định cho tài liệu Word tiếng Việt**: Calibri, Calibri Light, Segoe UI, Cambria.
- **Font an toàn**:
  - Với file `.docx`: dùng **Arial** hoặc **Times New Roman**.
  - Với file Biên bản họp `.html`: dùng **Montserrat** (Google Fonts weight 400/700 theo đúng chuẩn `meeting-note`).

## Báo cáo kết quả

Khi trình bày kết quả rà soát cho người dùng, dùng bảng ngắn gọn:

| Vị trí | Sai | Đúng | Loại lỗi |
|---|---|---|---|
| Phần 2, Bước 3 | ... | ... | Thiếu dấu / Nhầm danh xưng Anh-Chị |

Nếu không phát hiện lỗi nào, báo ngắn gọn: "Đã rà soát toàn bộ tài liệu, không phát hiện lỗi chính tả và danh xưng." — không cần liệt kê dài dòng.
