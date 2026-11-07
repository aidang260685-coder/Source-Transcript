---
name: harness-engineering
description: Kiểm tra, thiết kế và xây dựng hệ thống AI theo mô hình Harness Engineering với vòng lặp 5 bước khép kín GATHER (thu thập), CURATE (sàng lọc vào cửa sổ ngữ cảnh), ACT (thực thi công cụ qua bộ điều phối), VERIFY (kiểm chứng độc lập), RETRY (tự sửa lỗi). Dùng skill này bất cứ khi nào người dùng nhắc đến harness, agent loop, vòng lặp agent, kiến trúc agent, context window/ngân sách token, tool orchestration, verify/evaluator, retry/self-correction, chống ảo giác (hallucination) cho pipeline AI, hoặc muốn kiểm tra xem dự án đã có hệ thống agent đúng chuẩn chưa, hoặc dựng khung pipeline AI mới, kể cả khi họ không dùng đúng từ "Harness Engineering".
---

# Harness Engineering

Harness là lớp kỹ thuật bao quanh model: model chỉ là một thành phần, còn độ tin cậy, chi phí và độ trễ do harness quyết định. Skill này giúp kiểm tra một dự án đã có harness chưa, và nếu chưa thì dựng một khung chạy được, có test.

## Quy trình làm việc

### Bước 1: Kiểm tra trước, không giả định
Luôn kiểm tra hiện trạng trước khi xây. Dự án có thể đã có một phần.

```bash
python <skill>/scripts/audit_harness.py <thư_mục_dự_án>
```
Script quét 5 pha và 4 cổng an toàn (ghi vết, trần chi phí, test, cổng xuất bản), in `COMPLETE`, `PARTIAL` hoặc `ABSENT`.

Kết quả chỉ là tín hiệu từ khoá. Với mỗi pha có dấu hiệu, đọc code để xác nhận nó thật sự làm đúng việc, rồi đối chiếu bảng "Tiêu chí đạt" bên dưới. Báo cáo cho người dùng: pha nào có, pha nào thiếu, pha nào có nhưng yếu.

### Bước 2: Chọn hướng
- `ABSENT`: dựng mới bằng `scaffold_harness.py` (bước 3).
- `PARTIAL`: chỉ bổ sung pha thiếu và cổng an toàn thiếu, giữ nguyên code đang chạy. Đọc `references/architecture.md` để khớp hợp đồng giữa các pha.
- `COMPLETE`: rà chất lượng theo bảng tiêu chí và đề xuất cải tiến có đo đạc.

### Bước 3: Dựng khung
```bash
python <skill>/scripts/scaffold_harness.py <thư_mục_đích>
cd <thư_mục_đích> && python examples/demo.py && python -m unittest discover -s tests
```
Lõi dùng stdlib, chạy offline với `ScriptedLLM`. Để chạy thật, thay bằng `AnthropicClient()` (cần `pip install anthropic` và `ANTHROPIC_API_KEY`). Chạy test ngay sau khi dựng để biết nền tảng sạch trước khi tuỳ biến.

### Bước 4: Tuỳ biến cho bài toán của người dùng
Làm theo thứ tự này, chạy test sau mỗi thay đổi:
1. **Nguồn dữ liệu** (`gather.py`): thêm `Source` cho API/DB/web của họ. Web scraper phải có allowlist domain và tôn trọng robots.txt/điều khoản của trang.
2. **Công cụ** (`act.py`): đăng ký `Tool` với `required` và `timeout`. Công cụ có tác dụng phụ đặt `side_effects=True`.
3. **Tiêu chí kiểm chứng** (`verify.py`): thêm check riêng cho miền nghiệp vụ. Đây thường là chỗ tạo ra giá trị nhiều nhất.
4. **Ngân sách** (`harness.toml`, `CurateConfig`): chỉnh sau khi có số liệu từ `runs/*.jsonl`, đừng đoán.

## Năm pha và tiêu chí đạt

| Pha | Việc cần làm | Đạt khi |
|---|---|---|
| GATHER | Thu thô từ nhiều nguồn, song song | Mỗi mẩu có `source`/`uri`/thời gian; một nguồn lỗi không làm sập cả vòng; có timeout; nguồn web có allowlist |
| CURATE | Lọc nhiễu, khử trùng lặp, chấm điểm, đóng gói | Tổng token không bao giờ vượt `window`; có `output_reserve`; ghi `dropped` kèm lý do; có sổ cái token mỗi lần chạy |
| ACT | Model đề xuất, bộ điều phối thực thi | Chỉ chạy công cụ trong allowlist; kiểm tra tham số; có timeout; lỗi công cụ trả về như quan sát |
| VERIFY | Chấm độc lập trước khi xuất bản | Có check tất định (trích dẫn có thật, số liệu có căn cứ); giám khảo LLM tách riêng; check hỏng = không đạt |
| RETRY | Phát hiện sai lệch và sửa | Feedback cụ thể; phân loại lỗi; phát hiện dậm chân; có trần số lần, thời gian, token; hết lượt thì escalate |

Cổng xuất bản: chỉ `RunResult.publishable` (status `verified`) mới được đi ra ngoài. Không có ngoại lệ, kể cả khi "gần đạt".

## Nguyên tắc cốt lõi (kèm lý do)

- **Cửa sổ ngữ cảnh là bộ đệm CPU mới.** Mọi token đều tốn latency, tiền và độ chính xác, nên CURATE phải chủ động loại bỏ thay vì nhồi cho đủ. Câu "quyết định 70% hiệu năng" là quy tắc kinh nghiệm để nhớ; đừng trích như số đo, hãy đo trên hệ thống thật.
- **Bằng chứng có id, câu trả lời phải trích id.** Việc này biến "model có bịa không" thành phép kiểm tra tất định mà VERIFY làm được rẻ và chắc.
- **Kiểm chứng phải độc lập với người tạo ra.** Model tự chấm bài mình thường thiên vị; ưu tiên check bằng code, sau đó mới tới giám khảo LLM riêng.
- **Retry có chẩn đoán, không chạy lại mù quáng.** Thiếu bằng chứng cần thu thêm; sai diễn đạt chỉ cần feedback. Lỗi lặp lại thì dừng và chuyển cho con người, vì thử lại thêm chỉ đốt chi phí.
- **Mọi thứ đều có trần cứng.** Số lần thử, thời gian, token, ngân sách ngữ cảnh. Vòng lặp tự động không có trần sẽ có ngày chạy lạc.
- **Không đo thì không tối ưu.** Mỗi pha ghi JSONL theo `run_id`; chỉnh tham số dựa trên `utilization`, tỉ lệ retry, tỉ lệ escalate.

## Cấu trúc skill
```
harness-engineering/
├── SKILL.md
├── scripts/
│   ├── audit_harness.py      kiểm tra dự án có harness chưa
│   └── scaffold_harness.py   dựng dự án mới từ lõi tham chiếu
├── references/
│   ├── architecture.md       sơ đồ, bản đồ module, hợp đồng giữa các pha, quyết định thiết kế
│   ├── context-budget.md     quản lý cửa sổ ngữ cảnh, bảng chẩn đoán
│   └── verification.md       viết check mới, quy tắc retry, chỉ số theo dõi
└── assets/harness_core/      mã nguồn tham chiếu + 18 test + demo
```
Đọc `references/architecture.md` khi sửa hợp đồng giữa các pha, `context-budget.md` khi tối ưu chi phí/độ trễ, `verification.md` khi thêm check hoặc chỉnh chính sách retry.

## Khi trả lời người dùng
Nêu rõ kết quả kiểm tra (có/chưa có, thiếu pha nào) trước khi nói đến thiết kế. Nói thẳng những gì chưa được kiểm chứng thật (ví dụ chưa chạy với model thật hoặc nguồn dữ liệu thật của họ), thay vì để họ tưởng khung đã sẵn sàng production.
