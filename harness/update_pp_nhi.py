from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
# -*- coding: utf-8 -*-
"""
Chuẩn hoá nhân sự thuyết trình bộ phận Mua hàng (PP):
Chị Linh Nhi (PP) là người thuyết trình và báo cáo chính;
Chị Như (PP) chỉ tham gia dự họp.
"""
from pathlib import Path
import re

FILES = [
    BASE_DIR / "output" / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html",
    BASE_DIR / "doc" / "transcripts" / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html"
]

def update_html(p: Path):
    text = p.read_text(encoding="utf-8")

    # 1. Bảng Section I: người báo cáo PP là Chị Linh Nhi (PP)
    text = text.replace(
        "<td>Chị Như (PP), Chị Linh Nhi (PP)</td>",
        "<td>Chị Linh Nhi (PP)</td>"
    )

    # 2. Tiêu đề mục II.2 PP: Người báo cáo là Chị Linh Nhi (PP)
    text = text.replace(
        "2. Bộ phận Mua hàng &amp; Kế hoạch (PP) — Người báo cáo: Chị Như (PP) &amp; Chị Linh Nhi (PP)",
        "2. Bộ phận Mua hàng &amp; Kế hoạch (PP) — Người báo cáo: Chị Linh Nhi (PP)"
    )

    # 3. Thay các phát biểu/thảo luận của Chị Như (PP) thành Chị Linh Nhi (PP)
    text = text.replace("<li><strong>Chị Như (PP):</strong>", "<li><strong>Chị Linh Nhi (PP):</strong>")
    text = text.replace("mã hàng NACHI mà Như vừa nêu", "mã hàng NACHI mà Nhi vừa nêu")
    text = text.replace("Như hồi nãy em có trình bày", "Như hồi nãy em có trình bày") # giữ nguyên từ nối 'như'

    # 4. Bảng phân công Action Items (Section IV)
    text = text.replace(
        "<td><strong>Chị Thu (KT), Chị Như (PP), Sale</strong></td>",
        "<td><strong>Chị Thu (KT), Chị Linh Nhi (PP), Sale</strong></td>"
    )
    text = text.replace(
        "<td><strong>Sale &amp; PP (Chị Như, Anh Quang Tuẩn)</strong></td>",
        "<td><strong>Chị Linh Nhi (PP) &amp; Anh Quang Tuẩn (Sale)</strong></td>"
    )
    text = text.replace(
        "<td><strong>Anh Phương (QC) &amp; Chị Như (PP)</strong></td>",
        "<td><strong>Anh Phương (QC) &amp; Chị Linh Nhi (PP)</strong></td>"
    )

    p.write_text(text, encoding="utf-8")
    print(f"✅ Đã chuẩn hoá Chị Linh Nhi (PP) thuyết trình trong {p.name}")

for f in FILES:
    if f.exists():
        update_html(f)

# Cập nhật PP.txt
pp_file = BASE_DIR / "doc" / "transcripts" / "PP.txt"
if pp_file.exists():
    pp_txt = pp_file.read_text(encoding="utf-8")
    # Đổi các lượt nói thuyết trình từ [Chị Như (PP)] thành [Chị Linh Nhi (PP)]
    pp_txt = pp_txt.replace("[Chị Như (PP)]", "[Chị Linh Nhi (PP)]")
    pp_file.write_text(pp_txt, encoding="utf-8")
    print("✅ Đã cập nhật lượt nói người thuyết trình thành [Chị Linh Nhi (PP)] trong PP.txt")

# Cập nhật 00_DANH_MUC_TRANSCRIPT.md
dm_file = BASE_DIR / "doc" / "transcripts" / "00_DANH_MUC_TRANSCRIPT.md"
if dm_file.exists():
    dm_txt = dm_file.read_text(encoding="utf-8")
    dm_txt = dm_txt.replace("`Chị Như (PP)`, `Chị Linh Nhi (PP)`", "`Chị Linh Nhi (PP)` (thuyết trình chính), `Chị Như (PP)`")
    dm_file.write_text(dm_txt, encoding="utf-8")
    print("✅ Đã cập nhật 00_DANH_MUC_TRANSCRIPT.md")
