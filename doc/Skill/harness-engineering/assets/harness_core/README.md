# Harness core

```
python examples/demo.py                 # chạy offline, thấy VERIFY bắt số bịa và RETRY sửa
python -m unittest discover -s tests -v # chạy test
```
Thay `ScriptedLLM` bằng `AnthropicClient()` để chạy thật. Xem `references/` của skill để biết nguyên tắc thiết kế.
