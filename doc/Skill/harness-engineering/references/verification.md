# Kiểm chứng độc lập (pha VERIFY) và thử lại (pha RETRY)

## Vì sao "độc lập"
Model tự chấm bài mình viết thường thiên vị. Ba cách tạo độc lập, theo thứ tự ưu tiên:
1. **Check tất định bằng code** (schema, trích dẫn có thật, số liệu có trong bằng chứng, mẫu cấm). Rẻ, lặp lại được, không bị thuyết phục.
2. **Giám khảo LLM riêng**: client/prompt khác, chỉ nhận task + bằng chứng + bản nháp, không nhận lý lẽ trung gian. Dùng cho tiêu chí mềm (đủ ý, giọng văn).
3. **Con người** cho trường hợp `escalated`.

## Thêm một check mới
```python
class MyCheck:
    name = "my_check"
    def run(self, task, ctx, draft) -> CheckResult:
        ok = ...  # kiểm tra tất định
        return CheckResult(self.name, ok, message="..." if not ok else "",
                           fix_hint="bảo model sửa gì", needs_evidence=False)
```
- Đặt `needs_evidence=True` khi lỗi do thiếu dữ kiện (retry sẽ thu thêm thay vì chỉ viết lại).
- `severity="warn"` để ghi nhận mà không chặn.
- Viết test cho cả ca đạt và ca trượt của check mới.

## Quy tắc cho RETRY
- Phản hồi phải **cụ thể và có thể hành động** (`feedback()` gồm tên check, lỗi, gợi ý sửa).
- **Phân loại trước khi thử lại**: thiếu bằng chứng → regather + widen; lỗi diễn đạt → chỉ feedback.
- **Phát hiện dậm chân** bằng `signature`; đổi chiến lược một lần, nếu vẫn lặp thì `escalated`.
- **Trần cứng**: `max_attempts`, `max_seconds`, `max_total_tokens`. Retry không giới hạn là rò rỉ chi phí.
- Hết lượt thì giữ bản tốt nhất để con người xem, **nhưng không bao giờ publishable**.

## Chỉ số cần theo dõi
Tỉ lệ đạt ngay lần 1, số lần thử trung bình, tỉ lệ escalate, check nào trượt nhiều nhất, token mỗi lần chạy thành công.
