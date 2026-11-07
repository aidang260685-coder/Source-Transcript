from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
# -*- coding: utf-8 -*-
"""
Sửa triệt để lỗi gán nhầm bộ phận cho Chị Thu:
- HR CHỈ CÓ DUY NHẤT 1 NGƯỜI: Chị Ngọc (HR) - Trưởng bộ phận.
- CHỊ THU LÀ KẾ TOÁN: Chị Thu (KT) thuộc team Kế toán.
"""
from pathlib import Path
import re

FILES = [
    BASE_DIR / "output" / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html",
    BASE_DIR / "doc" / "transcripts" / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html"
]

def fix_file(p: Path):
    text = p.read_text(encoding="utf-8")

    # 1. Danh sách tham dự: HR chỉ có 1 người duy nhất là Chị Ngọc (HR)
    text = re.sub(
        r"•\s*<strong>HR\s*\([^)]*\):</strong>\s*Chị Ngọc \(HR\)[^<]*?<br>",
        "• <strong>HR (Bộ phận Nhân sự):</strong> Chị Ngọc (HR) — Trưởng bộ phận Nhân sự.<br>",
        text
    )

    # 2. Bảng tổng quan Section I hàng Nhân sự (HR): người báo cáo chỉ là Chị Ngọc (HR)
    text = re.sub(
        r"<td><strong>Nhân sự \(HR\)</strong></td>\s*<td>Chị Ngọc \(HR\),\s*Chị Thu \(HR\)</td>",
        "<td><strong>Nhân sự (HR)</strong></td>\n      <td>Chị Ngọc (HR)</td>",
        text
    )

    # 3. Tiêu đề tiểu mục 5 Section II: chỉ có Chị Ngọc (HR) báo cáo
    text = re.sub(
        r'<div class="subsection-title">5\.\s*Bộ phận Nhân sự \(HR\)\s*—\s*Người báo cáo:\s*Chị Ngọc \(HR\)\s*&amp;\s*Chị Thu \(HR\)</div>',
        '<div class="subsection-title">5. Bộ phận Nhân sự (HR) — Người báo cáo: Chị Ngọc (HR)</div>',
        text
    )

    # 4. Đoạn thảo luận chi phí công tác Sale: BOD giao Chị Thu (KT) phối hợp Chị Ngọc (HR)
    text = text.replace(
        "BOD yêu cầu Chị Thu (HR)",
        "BOD yêu cầu Chị Thu (KT) phối hợp với Chị Ngọc (HR)"
    )
    text = text.replace(
        "Chị Thu (HR) ghi nhận",
        "Chị Thu (KT) ghi nhận"
    )

    # 5. Bảng phân công Action Items Section IV: Chị Thu (KT) & Chị Ngọc (HR)
    text = text.replace(
        "<td><strong>Chị Thu (HR)</strong></td>",
        "<td><strong>Chị Thu (KT) &amp; Chị Ngọc (HR)</strong></td>"
    )

    p.write_text(text, encoding="utf-8")
    print(f"✅ Đã chuẩn hoá dứt điểm Chị Thu (KT) và Chị Ngọc (HR) trong: {p.name}")

for f in FILES:
    if f.exists():
        fix_file(f)

# Cập nhật Hr.txt
hr_file = BASE_DIR / "doc" / "transcripts" / "Hr.txt"
if hr_file.exists():
    hr_txt = hr_file.read_text(encoding="utf-8")
    hr_txt = hr_txt.replace("[Chị Thu (HR)]", "[Chị Thu (KT)]")
    hr_txt = hr_txt.replace("Chị Thu (HR) ghi nhận", "Chị Thu (KT) ghi nhận")
    hr_file.write_text(hr_txt, encoding="utf-8")
    print("✅ Đã cập nhật chuẩn hoá trong Hr.txt")
