import re
from pathlib import Path

p = Path(r"d:\Source-Transcript\output\Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html")
text = p.read_text(encoding="utf-8")
for m in re.finditer(r'<div class="subsection-title">.*?</div>', text):
    print(m.group(0))
