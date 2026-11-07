# Kiến trúc Harness

## Mục lục
1. Sơ đồ tổng thể
2. Bản đồ module
3. Hợp đồng giữa các pha
4. Quyết định thiết kế và lý do
5. Mở rộng lên production

## 1. Sơ đồ tổng thể

```
            ┌────────────────────────── Harness.run(task) ──────────────────────────┐
            │                                                                       │
 Nguồn ───► │ 1 GATHER ──► 2 CURATE ──► 3 ACT ──► 4 VERIFY ──pass──► publishable    │
 API/DB/Web │ (thô+nguồn   (lọc, dedupe,  (model đề  (độc lập,      │               │
            │  gốc)         chấm điểm,     xuất, bộ    fail-closed)  fail            │
            │               đóng gói theo   điều phối                 ▼              │
            │               ngân sách)      thực thi)            5 RETRY             │
            │                 ▲                                  ├─ thiếu bằng chứng: regather + widen
            │                 └──────── feedback có cấu trúc ◄───┤─ lỗi lặp lại: đổi chiến lược
            │                                                    └─ vượt trần / dậm chân: escalate
            └────────────────────── Tracer ghi JSONL mọi pha ───────────────────────┘
```

## 2. Bản đồ module (`harness/`)

| File | Pha | Trách nhiệm | Không được làm |
|---|---|---|---|
| `gather.py` | 1 | Thu song song, timeout, retry theo nguồn, gắn provenance | Lọc/tóm tắt |
| `curate.py` | 2 | Làm sạch, khử trùng lặp, BM25, quota nguồn, đóng gói theo ngân sách, nén trích xuất | Gọi model, vượt window |
| `act.py` | 3 | Vòng lặp tool-use, allowlist, kiểm tra tham số, timeout | Để model chạm thẳng hệ thống ngoài |
| `verify.py` | 4 | Check tất định + giám khảo LLM riêng, fail-closed | Xem lý lẽ trung gian của actor |
| `loop.py` | 5 + điều phối | RetryPolicy, phát hiện dậm chân, trần chi phí, cổng xuất bản, Tracer | Cho kết quả chưa verified đi tiếp |
| `models.py` | - | Dataclass dùng chung | Chứa logic |
| `llm.py` | - | Giao diện `LLMClient` + Anthropic + ScriptedLLM | Gắn chặt một nhà cung cấp |

## 3. Hợp đồng giữa các pha

- GATHER → CURATE: `list[RawItem]`, mỗi mẩu có `source`, `uri`, `fetched_at`.
- CURATE → ACT: `ContextPack` gồm `evidence[]` có id ngắn (`e1`..), sổ cái token `used` và danh sách `dropped` kèm lý do.
- ACT → VERIFY: `Draft` gồm `answer`, `citations[]` (id bằng chứng), `tool_records[]`.
- VERIFY → RETRY: `Verdict` có `failures`, `signature` (vân tay lỗi), `needs_evidence`, `feedback()`.
- RETRY → CURATE: `feedback` chèn vào task, `widen` nới hạn mức theo nguồn.

## 4. Quyết định thiết kế và lý do

- **Id bằng chứng ngắn + bắt buộc trích dẫn.** Biến "model có bịa không" thành bài toán kiểm tra tất định.
- **Nén trích xuất, không nén bằng tóm tắt sinh.** Giữ nguyên câu gốc thì không thêm sai lệch mới; tóm tắt bằng LLM vừa tốn một lần gọi vừa có thể méo dữ kiện.
- **window là trần cứng.** `widen` chỉ nới quota theo nguồn và ngưỡng điểm; không bao giờ nới tổng token.
- **Fail-closed.** Check bị lỗi hoặc giám khảo trả JSON hỏng đều tính là không đạt.
- **Phân loại lỗi trước khi retry.** Thiếu bằng chứng thì thu thêm; sai cách diễn đạt thì chỉ cần feedback. Retry mù quáng chỉ đốt tiền.
- **Dậm chân thì dừng sớm.** Cùng `signature` hai lần liên tiếp sau khi đã đổi chiến lược → `escalated` cho con người.
- **Một cổng xuất bản duy nhất:** `RunResult.publishable`. Mọi đường ra ngoài phải đi qua nó.
- **Lõi chỉ dùng stdlib.** Thay thế từng khối (BM25 → vector search, thread → asyncio) mà không phải đụng pha khác.

## 5. Mở rộng lên production

| Nhu cầu | Cách làm |
|---|---|
| Đếm token chính xác | Truyền `counter=` vào `Curator` (tokenizer của nhà cung cấp) |
| Truy hồi ngữ nghĩa | Thêm `VectorSource` ở GATHER hoặc thay `_score` bằng embedding + rerank |
| Tool có tác dụng phụ | Đặt `side_effects=True`, thêm idempotency key và bước duyệt trước khi chạy |
| Chạy song song nhiều task | Bọc `Harness.run` trong hàng đợi; Tracer đã tách theo `run_id` |
| Quan sát | Đẩy JSONL sang OpenTelemetry/Datadog; theo dõi `utilization`, tỉ lệ retry, tỉ lệ escalate |
| Cache | Cache theo `RawItem.id` ở GATHER; prompt caching cho `system` ở ACT |
