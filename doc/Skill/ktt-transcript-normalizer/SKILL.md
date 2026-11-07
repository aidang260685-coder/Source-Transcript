---
name: ktt-transcript-normalizer
description: Nghe trực tiếp file ghi âm (.m4a, .mp3, .wav) và chuẩn hoá transcript tiếng Việt có gắn nhãn người nói chuẩn xác theo danh sách nhân sự, bộ phận, thuật ngữ hệ thống (MISA AMIS) và mã hàng của Công ty TNHH Kiên Thành Tín (KTT). Dùng skill này bất cứ khi nào xử lý âm thanh cuộc họp, bóc băng ghi âm, chuẩn hoá lời thoại sang văn phong biên bản công sở, hoặc đối chiếu nhân sự/thuật ngữ trước khi lập biên bản họp (meeting-note).
---

# KTT Transcript Normalizer — Chuẩn Hoá Băng Ghi Âm & Định Danh Người Nói (Kiên Thành Tín)

Skill này thiết lập quy trình chuẩn để **nghe trực tiếp file âm thanh cuộc họp (`.m4a`)**, định danh chính xác người phát biểu theo từng phiên họp, chuẩn hoá thuật ngữ đặc thù ngành vòng bi – dây curoa và hệ thống quản trị nội bộ của **Công ty TNHH Kiên Thành Tín (KTT)**.

---

## 1. Nguyên Tắc Cốt Lõi (Zero Hallucination & Direct Audio Inspection)

1. **Nghe trực tiếp toàn bộ thời lượng file âm thanh**:
   - Bắt buộc dùng công cụ đọc file (`read_file`) trên từng file `.m4a` trong `doc/ghi_am/` để nghe từ giây đầu tiên đến giây cuối cùng.
   - Không đoán nội dung qua tên file và không lược bỏ các phần thảo luận, phản biện liên bộ phận ở nửa sau băng ghi âm.
2. **Không bịa đặt thông tin**:
   - Giữ nguyên 100% sự thật về số liệu, tỷ lệ %, số tiền, mốc thời gian, tên người phụ trách và quyết định của BOD.
   - Tuyệt đối không gán nhầm lời của người này sang người khác hoặc thêm tên nhân sự không phát biểu trong buổi họp đó.
3. **Chuẩn hoá lời nói khẩu ngữ sang văn phong biên bản công sở**:
   - Lược bỏ từ đệm (*"à, ừm, kiểu như là, nói chung là, cái phần mà..."*), câu lặp, câu nói dở.
   - Chuyển đại từ xưng hô thân mật (*"mày - tao, chị - em, chế, tụi em, nó"*) sang định dạng chuẩn **`<Danh xưng Anh/Chị> <Tên> (<Tag Bộ phận>)`**.
4. **Bảo mật âm thanh & Dữ liệu nội bộ (Strict Security & Privacy)**:
   - File âm thanh (.m4a), nội dung trao đổi, mật khẩu hoặc số liệu kinh doanh là tài sản bảo mật của doanh nghiệp.
   - Tuyệt đối KHÔNG tự ý chia sẻ dữ liệu hoặc chuyển giao cho bất kỳ AI Agent nào khác. Bắt buộc phải có sự xác nhận (CONFIRM) trực tiếp từ người dùng.

---

## 2. Danh Bạ Nhân Sự & Bộ Phận Chuẩn Của Kiên Thành Tín (KTT)

Mọi lời thoại và biên bản phải sử dụng thống nhất danh xưng + tên + tag bộ phận dưới đây:

### A. Ban Giám Đốc (BOD)
- **`Chị Thanh (BOD)`**: Chủ trì cuộc họp, điều phối chất vấn, chốt định hướng chiến lược và phân công hành động (trong băng ghi âm các nhân sự thường gọi thân mật là *"Chị Thanh"* hoặc *"Chế"*).
- **`Anh Tuấn Tú (BOD)`**: Thành viên Ban Giám đốc (BOD).

### B. Khối Back-Office & Vận Hành (Các bộ phận báo cáo)
Danh sách chuẩn các bộ phận báo cáo:
**`Anh Ân (IT)`, `Anh Vũ (Kế toán)`, `Chị Thu (KT)`, `Chị Trâm (KTT)`, `Chị Dung (KT)`, `Anh Khiêm (KT)`, `Anh Phương (QC)`, `Anh Tân (Kho)`, `Anh Tuấn (Kho)`, `Chị Như (PP)`, `Chị Linh Nhi (PP)`, `Anh Quang (PP)`, `Anh Lộc (MKT)`, `Anh Duy (MKT)`, `Chị Mai (MKT)`, `Chị Ngọc (HR)`**

Chi tiết từng bộ phận:
- **IT (`It1.m4a`, `It2.m4a`)**:
  - **`Anh Ân (IT)`**: Trưởng bộ phận / Phụ trách IT (báo cáo chính về `AMIS CRM`, `AMIS Kế toán`, `App Kho`, `n8n`, `VPS`, bản quyền `Microsoft Office` & `Windows Server 2016`).
  - Nhân sự IT được nhắc tên hỗ trợ kỹ thuật/dưới kho: `Quốc`, `Sơn`.
- **Kế toán (`Kế toán.m4a`)**:
  - **`Anh Vũ (Kế toán)`** (hoặc `Anh Vũ (KT)`), **`Anh Khiêm (KT)`**, **`Chị Thu (KT)`**, **`Chị Trâm (KTT)`**, **`Chị Dung (KT)`**.
- **QC (`Qc.m4a`)**:
  - **`Anh Phương (QC)`**: Phụ trách Kiểm soát chất lượng (QC).
- **Kho (`Kho.m4a`)**:
  - **`Anh Tân (Kho)`**, **`Anh Tuấn (Kho)`**: Phụ trách Kho vận (báo cáo chính về vận hành Kho, `App Kho`, thời gian hoàn thành đơn hàng, phối hợp dự án tối ưu tồn Kho A).
- **Mua hàng / Planning (`PP.m4a`)**:
  - **`Chị Linh Nhi (PP)`** (hoặc `Chị Nhi (PP)`): Người thuyết trình chính của phòng PP, báo cáo chi tiết về cơ cấu tồn kho nhóm `ABC`, hiệu quả đàm phán mua hàng, mua hàng trong nước, cải tiến chất lượng dây và chuẩn hoá danh mục mã hàng.
  - **`Chị Như (PP)`**: Nhân sự Mua hàng / Planning (`PP`) tham gia dự họp và tiếp thu ý kiến chỉ đạo của Ban Giám đốc (không tham gia thuyết trình báo cáo).
  - **`Anh Quang (PP)`**: Nhân sự PP phối hợp với `Anh Ân (IT)` xây dựng Web App mua hàng trong nước.
- **Marketing (`Marketing.m4a`, `Marketing2.m4a`, `Chị Thanh chia sẻ cùng marketing.m4a` -> Gộp chung vào `Marketing.txt`)**:
  - **`Anh Lộc (MKT)`**, **`Anh Duy (MKT)`**, **`Chị Mai (MKT)`**.
- **Nhân sự (`Hr.m4a`)**:
  - **`Chị Ngọc (HR)`**: Báo cáo chính về Nhân sự, chính sách khuyến khích đào tạo nội bộ, định biên `Sale Admin` và phân tích dữ liệu tăng ca (`Overtime`) Quý 3.
  - Phối hợp liên bộ phận: **`Chị Thu (KT)`** (Kế toán tài chính & ngân sách) cùng phối hợp với `Chị Ngọc (HR)` rà soát khung chi phí hỗ trợ công tác Sale theo chỉ đạo của BOD.
- **Team Data (`DA.m4a`)**:
  - **`Chị Vy (DA)`**, **`Anh Phát (DA)`**: Hai thành viên thực hiện và trình bày báo cáo Team Data (Dự án tối ưu tồn Kho A đạt độ chính xác 90%–95%, chuẩn hoá cây thư mục & mã hoá dữ liệu), dưới sự dẫn dắt/hỗ trợ của `Anh Duy (MKT)`.

### C. Khối Kinh Doanh (`Sale`)
- **Kênh TMĐT / Online / Michelin (`Hân - TMĐT online.m4a`, `Thành - Michelin.m4a`)**:
  - **`Anh Thành (Sale)`**, **`Chị Gia Hân (Sale)`**.
- **Kênh Nhà máy - B2B (`Tài - nhà máy.m4a`, `Chị Thanh nhận xét - kênh nhà máy.m4a`)**:
  - **`Anh Tài (Sale)`**.
- **Kênh Đại lý - Dealer (`Đại lý.m4a`)**:
  - **`Anh Quang Tuẩn (Sale)`**, **`Chị Bích Vi (Sale)`**, **`Chị Bích Vân (Sale)`**.
- **Lưu ý phân biệt người hỏi theo buổi họp**:
  - **`Anh Hùng (Sale)`**: Chỉ tham gia đặt câu hỏi ở **Buổi 1**, **KHÔNG** đặt câu hỏi ở **Buổi 2** (tuyệt đối không gán nhầm giọng của `Anh Quang Tuẩn (Sale)`, `Anh Thành (Sale)` hay `Anh Tài (Sale)` ở Buổi 2 thành `Anh Hùng (Sale)`).

---

## 3. Từ Điển Thuật Ngữ Hệ Thống & Mã Hàng Chuẩn (Domain Glossary)

Khi phiên âm hoặc biên tập, bắt buộc chuẩn hoá chính xác các thuật ngữ sau:

1. **Hệ thống Phần mềm & Công nghệ (Tuyệt đối KHÔNG viết nhầm thành `Bitrix`)**:
   - Hệ sinh thái MISA: **`MISA AMIS`**, **`AMIS CRM`**, **`AMIS Kế toán`** (Sổ Thuế & Sổ Nội bộ), **`AMIS Quy trình`**. *(Khi người nói phát âm "A-mít" hoặc nói tắt quy trình/kế nhiệm trên hệ thống, phải ghi đúng là **`AMIS`**, tuyệt đối không suy diễn thành `Bitrix` hay `Bitrix24`)*.
   - Các công cụ khác: **`App Kho`** (Web App & Mobile App), **`Kami`** (công cụ hỗ trợ lên đơn qua tin nhắn dừng vào cuối tháng 11), **`n8n`** (tự động hoá workflow dựng trên **`VPS`** nội bộ), **`Power BI`**, **`SQL Server`**, **`Windows Server 2016`**, **`File Server`**, **`Microsoft Office`**.
2. **Thương hiệu & Mã hàng (Vòng bi / Dây curoa / Phụ tùng)**:
   - Thương hiệu chuẩn: **`NACHI`** *(tuyệt đối không viết là "Natri")*, **`KYO`** *(tuyệt đối không viết là "KIO")*, **`WIN`**, **`Koyo`**, **`ASAHI`**, **`PIX`**, **`Cana`** *(không viết "Kana")*, **`Roleco`** *(không viết "Rulico")*, **`Michelin`**, **`Yamatron`**, **`Yamaran`**, **`Takatron`**, **`Takaran`**, **`NTN`**, **`SKF`**, **`NSK`**, **`Mitsuboshi`**.
   - Mã hàng cụ thể: **`NTN 6308CM`**, **`N260 326 K9`**, dây curoa **`B107`** / **`B66`** / **`B54`** / **`A38`** / **`A36`** / **`C120`** / **`C114`**.
3. **Thuật ngữ Vận hành & Quản trị**:
   - `lot/lô` (batch/lot truy xuất nguồn gốc), `packing list`, `QR Code`, `master data`, `lead time`, `overtime` (tăng ca), `credit` (tín chỉ đào tạo nội bộ), `LDP` (chương trình đào tạo Leader), `ISO`.

---

## 4. Định Dạng Đầu Ra Của Transcript Chuẩn Hoá & Quy Tắc Gom File Chống Bỏ Sót

1. **Cấu trúc dòng chuẩn trong mỗi file Transcript**:
   ```text
   ===== <Tên file ghi âm> (MM:SS -> MM:SS) =====
   [HH:MM:SS] [<Danh xưng Anh/Chị> <Tên> (<Tag Bộ phận>)] <Nội dung phát biểu đã được chuẩn hoá câu chữ, giữ nguyên 100% ý nghĩa, số liệu và thuật ngữ chuẩn>
   ```
2. **Quy tắc Gộp file ghi âm cùng phòng ban (`Multi-File Consolidation`)**:
   - Khi một bộ phận có nhiều file ghi âm liên tiếp (ví dụ: `It1.m4a` + `It2.m4a` -> **`IT.txt`**; `Marketing.m4a` + `Marketing2.m4a` + `Chị Thanh chia sẻ cùng marketing.m4a` -> **`Marketing.txt`**; `Tài - nhà máy.m4a` + `Chị Thanh nhận xét - kênh nhà máy.m4a` -> **`Tài - nhà máy.txt`**), bắt buộc gộp chung theo đúng trình tự thời gian vào **01 file transcript duy nhất của bộ phận đó**, ngăn cách bằng dòng tiêu đề `===== <Tên file .m4a> (MM:SS -> MM:SS) =====`.
3. **Quy tắc Chống bỏ sót thông tin khi lập Biên bản họp (`Meeting Note`)**:
   - Luôn duy trì và đối chiếu bảng chỉ mục `00_DANH_MUC_TRANSCRIPT.md` trong thư mục `doc/transcripts/`.
   - Trước khi tạo `Meeting Note`, AI bắt buộc kiểm tra đủ số lượng file trong `00_DANH_MUC_TRANSCRIPT.md` và đọc từ dòng đầu tiên đến dòng cuối cùng của từng file transcript (bao gồm tất cả các phân đoạn `===== ... =====` đã gộp bên trong).
4. **Kiểm tra Unicode NFC**:
   - Sau khi tạo hoặc cập nhật file transcript/biên bản, luôn kiểm tra chuẩn UTF-8 NFC (`FormC`).
