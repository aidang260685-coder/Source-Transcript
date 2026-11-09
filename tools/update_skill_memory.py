# -*- coding: utf-8 -*-
"""
update_skill_memory.py - Cập nhật tri thức nghiệp vụ và quy ước thư mục vào các file Skill
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Update harness-engineering/SKILL.md
he_path = BASE_DIR / "doc" / "Skill" / "harness-engineering" / "SKILL.md"
lines = he_path.read_text(encoding="utf-8").splitlines(keepends=True)
for i, l in enumerate(lines):
    if l.startswith("Cổng xuất bản:"):
        lines[i] = (
            "Cổng xuất bản: chỉ `RunResult.publishable` (status `verified`) mới được đi ra ngoài "
            "và bắt buộc lưu trữ tại thư mục **`output/`** (ví dụ: `output/Bien_Ban_Hop_[TieuDe]_[DD-MM-YYYY]_Verified.html`). "
            "Không có ngoại lệ, kể cả khi \"gần đạt\".\n\n"
            "### Bản đồ Thư mục Chuẩn (Directory Mapping) của Hệ thống:\n"
            "- **`doc/ghi_am/`**: Dữ liệu âm thanh thô thu thập ban đầu (Pha GATHER - Local Only).\n"
            "- **`doc/transcripts/`**: Dữ liệu bóc băng, sàng lọc và bảng chỉ mục kiểm soát (Pha CURATE).\n"
            "- **`harness/`**: Mã nguồn điều phối các pha và bộ kiểm chứng độc lập (Pha ACT & VERIFY).\n"
            "- **`output/`**: Cổng xuất bản chính thức lưu trữ các ấn phẩm hoàn chỉnh đã qua kiểm định (Publishable Gate).\n"
            "- **`runs/`**: Nhật ký chu trình JSONL truy vết toàn bộ quá trình tự hành.\n"
        )
        break
he_path.write_text("".join(lines), encoding="utf-8")
print("1. Updated harness-engineering/SKILL.md OK")

# 2. Update AGENTS.md and GEMINI.md
agents_path = BASE_DIR / "AGENTS.md"
gemini_path = BASE_DIR / "GEMINI.md"

agents_text = agents_path.read_text(encoding="utf-8")
if "output/" not in agents_text:
    agents_text = agents_text.replace(
        "- [`meeting-note`](./doc/Skill/meeting-note/SKILL.md): Tạo và cập nhật biên bản họp HTML chuẩn in PDF A4",
        "- [`meeting-note`](./doc/Skill/meeting-note/SKILL.md): Tạo và cập nhật biên bản họp HTML chuẩn in PDF A4 lưu tại `output/`"
    )
    agents_path.write_text(agents_text, encoding="utf-8")
    print("2. Updated AGENTS.md OK")

gemini_text = gemini_path.read_text(encoding="utf-8")
if "output/" not in gemini_text:
    gemini_text = gemini_text.replace(
        "6. Chuẩn cấu trúc biên bản 7 phần, cân bằng thẻ HTML.",
        "6. Chuẩn cấu trúc biên bản 7 phần, cân bằng thẻ HTML, lưu file tại cổng xuất bản `output/`."
    )
    gemini_path.write_text(gemini_text, encoding="utf-8")
    print("3. Updated GEMINI.md OK")

print("All skill memory updates complete!")
