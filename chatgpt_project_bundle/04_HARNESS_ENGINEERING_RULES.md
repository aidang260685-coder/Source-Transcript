# HỆ QUY TẮC HARNESS ENGINEERING (AUTONOMOUS VERIFICATION AUDIT)

Harness Engineering là kiến trúc kỹ thuật bao quanh mô hình ngôn ngữ lớn (LLM), biến một AI thông thường thành một hệ thống tự hành có khả năng tự kiểm chứng (Self-Verification), chống ảo giác (Zero Hallucination) và tự sửa sai (Self-Correction).

---

## 1. CHU TRÌNH 5 PHA KHÉP KÍN (HARNESS LIFECYCLE)

Mọi yêu cầu xử lý phức tạp phải trải qua đầy đủ 5 pha:

```
  [1. GATHER] ---> [2. CURATE] ---> [3. ACT] ---> [4. VERIFY] ---> [XUẤT BẢN]
                                                      |
                                                      +-- Lỗi / Mâu thuẫn
                                                      v
                                                 [5. RETRY]
```

1. **Pha 1 — GATHER (Thu thập có căn cứ)**:
   - Thu thập toàn bộ nội dung từ transcript, audio note, văn bản hoặc tài liệu đính kèm.
   - Gắn nhãn nguồn gốc cho từng phát biểu (Ai nói, thuộc bộ phận nào, ở mốc thời gian nào).
   - Tuyệt đối không lấy dữ liệu phỏng đoán ngoài tài liệu được cấp.
2. **Pha 2 — CURATE (Sàng lọc & Quản trị ngân sách ngữ cảnh)**:
   - Cửa sổ ngữ cảnh (Context Window) là tài nguyên hữu hạn và đắt giá. Pha Curate phải chủ động loại bỏ từ đệm, câu nói dở, các nội dung chào hỏi ngoài lề.
   - Phân loại dữ liệu thô vào 4 ngăn nghiệp vụ rõ ràng: Số liệu báo cáo, Vấn đề phản biện, Chỉ đạo của Lãnh đạo, Phân công công việc.
3. **Pha 3 — ACT (Thực thi & Tạo lập văn bản)**:
   - Soạn thảo tài liệu hoặc biên bản hoàn chỉnh theo đúng cấu trúc tiêu chuẩn được quy định.
   - Chuẩn hoá danh xưng, định dạng bảng biểu, văn phong công sở mạch lạc.
4. **Pha 4 — VERIFY (Kiểm chứng tất định — 6 Cổng an toàn)**:
   - Đây là pha quan trọng nhất. AI tự đóng vai trò Giám định viên độc lập (Auditor) để rà soát bản thảo qua 6 cổng kiểm tra toán học và logic (chi tiết ở mục 2).
5. **Pha 5 — RETRY (Tự sửa sai có chẩn đoán)**:
   - Nếu phát hiện bất kỳ Gate nào bị Fail, không chạy lại mù quáng mà chỉ ra chính xác điểm sai (Ví dụ: "Số liệu ở Section I không khớp Section II", "Deadline rơi vào Chủ nhật", "Chị Thu bị gán nhầm sang HR").
   - Tự động sửa lại bản thảo cho đến khi đạt 100% các Gate mới được bàn giao cho người dùng.

---

## 2. CHI TIẾT 6 CỔNG KIỂM CHỨNG TẤT ĐỊNH (THE 6 DETERMINISTIC GATES)

Trước khi gửi câu trả lời ra ngoài, bản thảo bắt buộc phải vượt qua toàn bộ 6 Gate:

### [GATE 1] Kiểm tra tính tự khớp toán học & Chú giải số liệu
- Tự tính toán lại toàn bộ các phép tính: Tỷ lệ %, phép chia, phép cộng cơ cấu.
  + Ví dụ: `15 / 2.648 = 0,57%` -> Tuyệt đối không được làm tròn bừa bãi thành `1%`.
  + Doanh số tổng phải bằng tổng các kênh con: `1,6 tỷ + 0,87 tỷ + 0,23 tỷ = 2,7 tỷ`.
- Nếu có hai số liệu nhìn bề ngoài giống nhau hoặc mâu thuẫn (như Tồn kho 28 tỷ, 33 tỷ, 37 tỷ), bắt buộc phải có chú giải rõ phạm vi từng con số (Ví dụ: 28 tỷ là kế hoạch Mua hàng, 33-37 tỷ là sổ sách Kế toán, >30 tỷ là hàng vật lý tại Kho).
- Tỷ lệ chốt đơn phải ghi rõ căn cứ tính (theo số lượng đơn hay theo giá trị tiền tệ).

### [GATE 2] Tính đồng bộ tuyệt đối giữa Bảng Tổng quan (I) và Chi tiết (II)
- Mọi chỉ số xuất hiện ở Bảng tóm tắt cốt lõi (Section I) đều PHẢI có dòng phân tích chi tiết, nguyên nhân và kế hoạch ở Section II.
- Không được đưa vào Bảng tổng quan những chỉ số "từ trên trời rơi xuống" mà không có trong nội dung báo cáo.

### [GATE 3] Phủ đủ 100% chỉ đạo và giao việc của Ban Giám Đốc (BOD)
- Rà soát toàn bộ các ý kiến chỉ đạo, chấn chỉnh, phân công của `Chị Thanh (BOD)` trong buổi họp.
- MỖI chỉ đạo của BOD đều PHẢI tương ứng với ít nhất một dòng hành động cụ thể trong Bảng phân công (Section IV).
- Không được bỏ sót các chỉ đạo quan trọng (như rà soát tồn kho B/C, đóng gói gộp đơn hàng, bỏ khâu kiểm lặp tại Kho, bóc tách giờ tăng ca, làm việc với nhà cung cấp, chuyển đổi hệ thống).

### [GATE 4] Chuẩn hoá Danh xưng, Giới tính & Tag bộ phận
- 100% tên nhân sự phải tuân thủ định dạng: `<Danh xưng Anh/Chị> <Tên> (<Tag Bộ phận>)`.
- Đúng danh xưng giới tính (Anh cho Nam, Chị cho Nữ). Không tự đoán bừa.
- Tất cả người được giao việc trong Bảng phân công (Section IV) đều phải có tên trong Danh sách thành phần tham dự.
- Không có lỗi lồng ngoặc thừa (ví dụ: `((...))` hoặc `(Chị Thanh (BOD))`).

### [GATE 5] Tính hợp lệ của Deadline
- Tất cả các mốc hạn hoàn thành (Deadline) phải là ngày làm việc cụ thể trong tuần: **Thứ Hai đến Thứ Sáu**.
- Tuyệt đối không để deadline rơi vào ngày cuối tuần (Thứ Bảy, Chủ Nhật). Nếu tính toán rơi vào cuối tuần, tự động dời sang Thứ Hai kế tiếp.
- Không dùng các hạn chót mơ hồ như "trong 7 ngày", "sớm nhất có thể", "tuần sau".

### [GATE 6] Kiểm soát cấu trúc, Thời gian họp & Cân bằng thẻ
- Biên bản phải ghi rõ ngày và giờ họp cụ thể (Ví dụ: `DD/MM/YYYY - HH:MM`). Nếu họp nhiều phiên, phải ghi đủ thời gian từng phiên.
- Cấu trúc 7 phần La Mã đầy đủ. Bảng biểu ngay ngắn, không bị đứt đoạn.
- Khi xuất ra HTML, cấu trúc thẻ đóng/mở phải hoàn toàn cân bằng.

---

## 3. NGUYÊN TẮC NIÊM PHONG "VERIFIED"
- Chỉ có các tài liệu vượt qua **100% (6/6 Gates PASSED)** mới được công nhận là bản hoàn thiện đạt chuẩn ("VERIFIED").
- Tài liệu này hoàn toàn đủ độ tin cậy để ban hành chính thức cho Ban Giám Đốc và các Trưởng bộ phận mà không cần đối soát lại thủ công.
