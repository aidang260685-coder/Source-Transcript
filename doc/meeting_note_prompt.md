# QUY TRÌNH 2 BƯỚC: TRANSCRIPT (.m4a) → BIÊN BẢN HỌP CHUYÊN NGHIỆP

Dùng sau khi chạy `transcribe_batch.py` và có file `ALL_transcripts.txt` (kèm `*_flagged.txt`).
Bạn có thể chạy trực tiếp với Agent trong workspace này (nhờ bộ skill `meeting-note` và `vietnamese-spellcheck` trong `doc/Skill\`) hoặc gửi cho AI theo 2 bước dưới đây.

---

## BƯỚC A - CHUẨN HOÁ TIẾNG VIỆT & DANH XƯNG (GENDER)

Dán nguyên khối này:

```markdown
Dưới đây là transcript thô của cuộc họp (tạo bằng AI từ file .m4a nên có lỗi nhận dạng).
Hãy chuẩn hoá thành văn bản tiếng Việt chuẩn mực, theo đúng các nguyên tắc nghiêm ngặt sau:

1. CHÍNH TẢ & DẤU THANH TIẾNG VIỆT:
   - Sửa lỗi dấu thanh, phụ âm đầu (ch/tr, s/x, d/gi/r, l/n), vần (iêc/iêt, ươc/ươt, an/ang...) và từ đồng âm sai ngữ cảnh (ví dụ: "phân tịch" -> "phân tích", "nghiệm thư" -> "nghiệm thu", "công lợ" -> "công nợ").
   - Thống nhất chuẩn Unicode dựng sẵn (NFC) và quy tắc đặt dấu thanh tiếng Việt nhất quán.
   - Thêm dấu câu chuẩn xác, viết hoa đầu câu và tên riêng, tách đoạn hợp lý theo luồng ý/người nói.

2. CHUẨN HOÁ DANH XƯNG & GIỚI TÍNH (GENDER) TIẾNG VIỆT:
   - Nhận diện và chuẩn hoá đúng danh xưng theo giới tính và vai vế trong tiếng Việt công sở: **Anh / Chị / Ông / Bà / Bạn / Em**.
   - Viết hoa danh xưng đi kèm tên riêng để thể hiện sự chuyên nghiệp và tôn trọng (ví dụ: `Anh Minh`, `Chị Hương`, `Anh Tuấn (IT)`).
   - Đối chiếu với danh sách Thành phần tham dự để KHÔNG bao giờ nhầm lẫn giới tính ("Anh" thành "Chị" hoặc ngược lại). Nếu transcript thô bị nhận nhầm (do giọng nói hoặc âm lướt như "chị Minh" trong khi Minh là Nam trong danh sách), phải sửa lại đúng theo danh sách tham dự; nếu chưa rõ giới tính của một tên người mới phát sinh, giữ nguyên và gắn `[cần xác nhận danh xưng: Anh/Chị]`.
   - Chuyển các đại từ khẩu ngữ trong lời nói trực tiếp ("mày/tao", "nó", "ông kia/bà kia") sang cách diễn đạt gián tiếp lịch sự, chuẩn văn phong biên bản ("Anh/Chị [Tên]", "bộ phận [Tên]", "nhân sự phụ trách") khi tóm tắt.

3. BẢO TOÀN SỰ THẬT (ZERO HALLUCINATION):
   - Giữ nguyên ý người nói. KHÔNG thêm ý, KHÔNG suy đoán, KHÔNG tự làm đẹp nội dung làm sai bản chất.
   - Tuyệt đối KHÔNG tự sửa hoặc bịa SỐ LIỆU, TIỀN TỆ, TỶ LỆ %, NGÀY THÁNG, DEADLINE, TÊN NGƯỜI. Nếu nghi ngờ, giữ nguyên và gắn `[cần kiểm tra]`.
   - Các đoạn có thẻ `[??]` là đoạn AI nghe kém chắc chắn: liệt kê riêng ở cuối (kèm mốc thời gian `[HH:MM:SS]`) để người duyệt nghe lại.

4. THUẬT NGỮ & TỪ ĐỆM:
   - Từ tiếng Anh/thuật ngữ chuyên ngành: viết đúng dạng chuẩn (AMIS, CRM, ERP, BOD, KPI, UAT, go-live, master data, Power BI...).
   - Lược bỏ từ đệm lặp vô nghĩa ("ờ", "à", "thì là", "kiểu như", "cái này cái kia") nhưng không làm thay đổi sắc thái khẳng định/phủ định/còn bỏ ngỏ của câu.

Danh sách thành phần tham dự (kèm danh xưng Anh/Chị):
[Điền danh sách: ví dụ: Anh Nguyễn Văn A - Giám đốc (BOD), Chị Trần Thị B - Kế toán trưởng (ACC)]

Danh sách thuật ngữ/tên riêng tham chiếu:
[Dán nội dung glossary.txt]
```

Kết quả: Bản transcript sạch + Bảng đối chiếu các đoạn `[??]` / `[cần kiểm tra]`. Kiểm tra nhanh trước khi sang Bước B.

---

## BƯỚC B - TẠO BIÊN BẢN HỌP CHUYÊN NGHIỆP (SKILL `meeting-note` & `vietnamese-spellcheck`)

Dán nguyên khối này:

```markdown
Dùng skill `meeting-note` và `vietnamese-spellcheck` (trong `doc/Skill/`) để tạo biên bản họp HTML chuẩn in A4 từ transcript đã chuẩn hoá ở trên.

THÔNG TIN CUỘC HỌP
- Tiêu đề: [ ]
- Ngày & giờ: [DD/MM/YYYY - HH:MM]
- Địa điểm / Hình thức: [Phòng họp ... / Online]
- Loại họp: [kickoff/triển khai | weekly/đánh giá vận hành | bsc_kpi/báo cáo quý BSC & KPI | không chắc]
- Chủ trì: [Anh/Chị Tên - Chức vụ (Tag bộ phận)]
- Thư ký: [Anh/Chị Tên - Chức vụ (Tag bộ phận)]
- Thành phần tham dự: [Anh/Chị Tên - Chức vụ - Tag Bộ phận, mỗi người một dòng]
- Tag bộ phận viết tắt: [ví dụ: BOD (Ban Giám đốc), WH (Kho), ACC (Kế toán), IT (CNTT), PUR (Mua hàng), SALE (Kinh doanh)]
- Agenda gốc (nếu có, đánh số mục): [dán, hoặc ghi "không có"]
- Tham chiếu cuộc họp trước: [nếu có]
- Người duyệt biên bản: [Anh/Chị Tên]

YÊU CẦU BẮT BUỘC
1. Chọn đúng khung cấu trúc (`kickoff/triển khai`, `weekly/đánh giá vận hành`, hoặc `bsc_kpi/báo cáo quý BSC & KPI`) theo mục tiêu cuộc họp. Với họp Báo cáo Quý (`khung_bsc_kpi.html`), tách riêng báo cáo BSC & KPI của từng bộ phận, kèm thảo luận liên phòng ban và khối đánh giá/chỉ đạo của BOD (`.bod-eval`) ngay sau mỗi bộ phận.
2. Nếu có Agenda đánh số: Phần II (Nội dung chi tiết) phải đủ và đúng thứ tự từng mục, không tự ý gộp hoặc đảo thứ tự.
3. Chuẩn danh xưng & Tag bộ phận: Mọi tên nhân sự xuất hiện trong biên bản đều phải có danh xưng đúng giới tính (`Anh`/`Chị`) + Tên + Tag bộ phận, ví dụ: `Anh Hùng (IT)`, `Chị Mai (ACC)`, nhất quán từ đầu đến cuối.
4. Phân loại trạng thái rõ ràng bằng hộp màu / nhãn trạng thái:
   - 🔴 Vấn đề còn mở / Rủi ro / Vướng mắc (Đỏ)
   - 🟡 Đã thảo luận / Phương án tạm thời (Vàng)
   - 🟢 Kết luận chốt & Hành động tiếp theo / Next Steps (Xanh lá)
   - 🔵 Lộ trình & Yêu cầu báo cáo định kỳ (Xanh dương nhạt)
5. Bảng phân công công việc (Action Items) đủ 5 cột chuẩn:
   `STT | Người phụ trách (Anh/Chị + Tag) | Công việc cụ thể (bắt đầu bằng động từ hành động) | Deadline | Ghi chú / Đầu ra (Deliverable)`
6. Mỗi ý trong biên bản phải có chủ thể rõ ràng + động từ hành động; mọi rủi ro nêu ra phải đi kèm hậu quả/tác động cụ thể.
7. KHÔNG bịa số liệu/deadline không có trong nguồn. Thiếu thông tin thì ghi rõ `Chưa xác định` và gom vào mục "Danh sách thông tin cần xác nhận bổ sung" ở cuối biên bản.
8. Gộp nội dung từ nhiều file ghi âm thành MỘT biên bản thống nhất theo trình tự thời gian/mạch nội dung, trừ khi được yêu cầu tách riêng.
```

---

## KIỂM TRA CUỐI (NGƯỜI DUYỆT TỰ LÀM - 5 PHÚT)

- [ ] Nghe lại các đoạn `[??]` / `[cần kiểm tra]` theo mốc thời gian
- [ ] Đối chiếu số liệu, tiền tệ, deadline, tên người với ghi chú gốc
- [ ] Kiểm tra danh xưng `Anh` / `Chị` (Gender) và Tag bộ phận của từng nhân sự đã chuẩn 100% chưa
- [ ] Mục `Chưa xác định` đã được điền bổ sung trước khi ký ban hành
- [ ] Xuất/In thử HTML sang PDF: bố cục gọn gàng, không quá 4 trang A4
