# Quản lý cửa sổ ngữ cảnh (pha CURATE)

Coi cửa sổ ngữ cảnh như bộ đệm CPU: nhỏ, đắt, quyết định phần lớn hiệu năng. Câu "70%" trong brief là
quy tắc kinh nghiệm để nhớ tầm quan trọng, không phải số đo; hãy đo trên hệ thống của bạn qua `runs/*.jsonl`.

## Sổ cái ngân sách

```
window = system + task + evidence + output_reserve        (+ safety_margin)
evidence_budget = (window - output_reserve) * (1 - safety_margin) - system - task
```
Đưa số này vào trace ở mỗi lần chạy: `used`, `utilization`, `dropped`.

## Thứ tự xử lý (rẻ → đắt)
1. **Làm sạch**: bỏ thẻ HTML, boilerplate (cookie, đăng ký nhận tin, quảng cáo), mẩu quá ngắn, nhiễu ký hiệu.
2. **Khử trùng lặp**: Jaccard trên shingle 3 từ, ngưỡng 0.8. Cùng một tin lặp ở 5 nguồn chỉ nên tốn token một lần.
3. **Chấm điểm**: BM25 rút gọn × trọng số nguồn. Thay bằng embedding/rerank khi cần ngữ nghĩa.
4. **Quota theo nguồn**: không để một nguồn ồn ào chiếm hết ngân sách.
5. **Nén trích xuất**: khi một mẩu quá lớn, giữ các câu khớp truy vấn nhất, giữ nguyên văn.
6. **Sắp xếp**: mẩu điểm cao đặt đầu; model chú ý kém ở giữa ngữ cảnh dài.

## Điều chỉnh khi đo được vấn đề

| Triệu chứng | Hướng xử lý |
|---|---|
| Latency/chi phí cao, `utilization` > 0.8 thường xuyên | Giảm `window` hoặc `max_per_source`, tăng `min_score` |
| Model nói "không đủ bằng chứng" dù dữ liệu có | Tăng `max_per_source`, hạ `min_score`, kiểm tra từ khoá `query` |
| Nhiều `near_duplicate` bị loại | Bình thường; nếu quá nhiều, xem lại nguồn có bị trùng lặp không |
| Tiếng Việt cắt cụt bất ngờ | `estimate_tokens` đã dùng hệ số bảo thủ; thay bằng tokenizer thật |

## Lỗi hay gặp
- Nhồi cả tài liệu vì "cửa sổ còn rộng". Rộng không có nghĩa là miễn phí hay không ảnh hưởng chất lượng.
- Nén bằng tóm tắt sinh rồi trích dẫn tóm tắt như thể là nguồn gốc.
- Quên chừa `output_reserve`, khiến câu trả lời bị cắt giữa chừng.
