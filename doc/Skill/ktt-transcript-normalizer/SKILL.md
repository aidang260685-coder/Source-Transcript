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
   - **Nếu môi trường không có công cụ nghe được âm thanh** (hoặc file không mở được), DỪNG và báo cho người dùng, tuyệt đối không bịa transcript từ tên file hay ngữ cảnh. Người dùng có thể cung cấp transcript chữ để tiếp tục.
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

Danh bạ này chỉ là **bảng tra cứu mặc định** (ai là ai, giới tính/danh xưng, tag bộ phận). Nó KHÔNG cho biết ai có mặt hay ai phát biểu trong một buổi họp cụ thể.

### 2.0. Thứ tự ưu tiên nguồn thông tin cho MỖI buổi họp
1. **Prompt của người dùng cho buổi họp đó** (danh sách tham dự, cách viết tên, buổi họp, ngữ cảnh): luôn thắng danh bạ.
2. **Lời tự giới thiệu hoặc được gọi tên trong chính băng ghi âm.**
3. **`doc/meeting_context.md`** của buổi họp đó (nếu người dùng có cung cấp).
4. **Danh bạ mặc định bên dưới**: dùng khi không có ba nguồn trên. Khi buổi họp không có prompt hay giới thiệu, giữ nguyên cách viết tên trong danh bạ và nêu các tên chưa được xác nhận ở danh sách bàn giao, không gắn cờ chen vào lời thoại.
- Mỗi buổi họp có ngữ cảnh riêng. Không mang thông tin của buổi họp này sang buổi khác (ai hỏi ở buổi nào, tên file ghi âm, dự án đang diễn ra, số liệu).
- Chỉ liệt kê người **có phát biểu hoặc được giao việc** trong buổi đó; có tên trong danh bạ không có nghĩa là có dự họp.

### A. Ban Giám Đốc (BOD)
- **`Chị Thanh (BOD)`**: thường chủ trì, điều phối chất vấn, chốt định hướng và phân công (nhân sự hay gọi thân mật là *"Chị Thanh"* hoặc *"Chế"*).
- **`Anh Tuấn Tú (BOD)`**: thành viên Ban Giám đốc.

### B. Khối Back-Office & Vận Hành
- **IT**: `Anh Ân (IT)` (phụ trách IT). Nhân sự IT có thể được nhắc tên khi hỗ trợ kỹ thuật: `Quốc`, `Sơn`.
- **Kế toán**: `Chị Thu (KT)` (kế toán tổng hợp), `Anh Vũ (Kế toán)` (hoặc `Anh Vũ (KT)`), `Anh Khiêm (KT)`, `Chị Trâm (KTT)`, `Chị Dung (KT)`.
- **Đối tác tư vấn Nidobiz (Nido)**: `Chị Thúy (Nido)` (trưởng nhóm tư vấn quản trị, tài chính, vận hành), `Chị Trang (KT - Nido)` (tư vấn kế toán).
- **QC**: `Anh Phương (QC)`.
- **Kho**: `Anh Tân (Kho)`, `Anh Tuấn (Kho)`.
- **Mua hàng / Planning (PP)**: `Chị Linh Nhi (PP)` (hoặc `Chị Nhi (PP)`), `Chị Như (PP)`, `Anh Quang (PP)`.
- **Marketing (MKT)**: `Anh Lộc (MKT)`, `Anh Duy (MKT)`, `Chị Mai (MKT)`.
- **Nhân sự (HR)**: `Chị Ngọc (HR)`.
- **Team Data (DA)**: `Chị Vy (DA)`, `Anh Phát (DA)`.

### C. Khối Kinh Doanh (Sale)
`Anh Thành (Sale)`, `Chị Gia Hân (Sale)`, `Anh Tài (Sale)`, `Anh Quang Tuẩn (Sale)`, `Chị Bích Vi (Sale)`, `Chị Bích Vân (Sale)`, `Anh Hùng (Sale)`.
- Kênh phụ trách (TMĐT/Online, Michelin, Nhà máy B2B, Đại lý) thay đổi theo kỳ: lấy từ prompt hoặc `doc/meeting_context.md` của buổi họp đó.

### D. Quy tắc phân biệt tên gần giống
- Các tên dễ nhầm khi nghe: `Anh Tuấn Tú (BOD)`, `Anh Tuấn (Kho)`, `Anh Quang (PP)`, `Anh Quang Tuẩn (Sale)`. Khi chỉ nghe tên gọi tắt ("Tuấn", "Quang"), căn cứ vào bộ phận đang báo cáo và nội dung phát biểu; nếu vẫn không chắc, ghi `[cần xác nhận người nói - HH:MM:SS]`, không tự gán.
- Cách viết `Quang Tuẩn` / `Quang Tuấn`: theo prompt hoặc lời giới thiệu trong buổi họp nếu có; nếu không có, giữ như danh bạ này và ghi vào danh sách bàn giao để người dùng xác nhận.

---

## 3. Từ Điển Thuật Ngữ Hệ Thống & Mã Hàng Chuẩn (Domain Glossary)

Khi phiên âm hoặc biên tập, bắt buộc chuẩn hoá chính xác các thuật ngữ sau:

1. **Hệ thống Phần mềm & Công nghệ (Tuyệt đối KHÔNG viết nhầm thành `Bitrix`)**:
   - Hệ sinh thái MISA: **`MISA AMIS`**, **`AMIS CRM`**, **`AMIS Kế toán`** (Sổ Thuế & Sổ Nội bộ), **`AMIS Quy trình`**. *(Khi người nói phát âm "A-mít" hoặc nói tắt quy trình/kế nhiệm trên hệ thống, phải ghi đúng là **`AMIS`**, tuyệt đối không suy diễn thành `Bitrix` hay `Bitrix24`)*.
   - Các công cụ khác: **`App Kho`** (Web App & Mobile App), **`Kami`** (công cụ hỗ trợ lên đơn qua tin nhắn), **`n8n`** (tự động hoá workflow dựng trên **`VPS`** nội bộ), **`Power BI`**, **`SQL Server`**, **`Windows Server 2016`**, **`File Server`**, **`Microsoft Office`**.
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
2. **Gắn cờ đoạn nghe không chắc**: đoạn có số liệu, tên riêng, mã hàng hoặc người nói chưa chắc chắn phải gắn `[??]` kèm mốc thời gian để người dùng xác nhận, không tự chọn một đáp án. Giữ nguyên mốc `[HH:MM:SS]` vì biên bản dùng nó làm tham chiếu dẫn chứng (`data-ref`).
3. **Quy tắc Gộp file ghi âm cùng phòng ban (`Multi-File Consolidation`)**:
   - Khi một bộ phận có nhiều file ghi âm liên tiếp (ví dụ: nhiều file của cùng một bộ phận như `<BoPhan>1.m4a` + `<BoPhan>2.m4a`, hoặc file nhận xét của BOD về bộ phận đó -> **`<BoPhan>.txt`**), bắt buộc gộp chung theo đúng trình tự thời gian vào **01 file transcript duy nhất của bộ phận đó**, ngăn cách bằng dòng tiêu đề `===== <Tên file .m4a> (MM:SS -> MM:SS) =====`.
4. **Quy tắc Chống bỏ sót thông tin khi lập Biên bản họp (`Meeting Note`)**:
   - Luôn duy trì và đối chiếu bảng chỉ mục `00_DANH_MUC_TRANSCRIPT.md` trong thư mục `doc/transcripts/`.
   - Trước khi tạo `Meeting Note`, AI bắt buộc kiểm tra đủ số lượng file trong `00_DANH_MUC_TRANSCRIPT.md` và đọc từ dòng đầu tiên đến dòng cuối cùng của từng file transcript (bao gồm tất cả các phân đoạn `===== ... =====` đã gộp bên trong).
5. **Kiểm tra Unicode NFC**:
   - Sau khi tạo hoặc cập nhật file transcript/biên bản, luôn kiểm tra chuẩn UTF-8 NFC (`FormC`).
