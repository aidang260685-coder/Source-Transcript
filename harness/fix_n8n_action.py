# -*- coding: utf-8 -*-
"""
Chỉnh sửa chính xác Action Item IT về n8n:
Anh Ân (IT) hướng dẫn Anh Duy (MKT) export workflow n8n từ cloud và import về VPS nội bộ.
"""
from pathlib import Path

FILES = [
    Path(r"d:\Source-Transcript\output\Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html"),
    Path(r"d:\Source-Transcript\doc\transcripts\Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html")
]

OLD_ACTION = """    <tr>
      <td><strong>Anh Ân (IT)</strong></td>
      <td>Chuyển đổi toàn bộ các workflow tự động hoá n8n và dữ liệu nhạy cảm từ hosting bên ngoài về máy chủ VPS nội bộ của công ty.</td>
      <td>20/11/2026</td>
      <td>IT; Đầu ra: Toàn bộ workflow n8n chạy trên VPS công ty.</td>
    </tr>"""

NEW_ACTION = """    <tr>
      <td><strong>Anh Ân (IT) &amp; Anh Duy (MKT)</strong></td>
      <td>Hướng dẫn team Marketing kết xuất (export) các workflow tự động hoá n8n từ bản cloud dùng thử và nạp (import) lên máy chủ VPS nội bộ của công ty (kèm cấu hình xác thực bảo mật authentication).</td>
      <td>13/11/2026</td>
      <td>IT &amp; MKT; Đầu ra: Workflow MKT chạy ổn định trên VPS công ty.</td>
    </tr>"""

def update():
    for p in FILES:
        if not p.exists(): continue
        text = p.read_text(encoding="utf-8")
        if "Chuyển đổi toàn bộ các workflow tự động hoá n8n" in text:
            text = text.replace(OLD_ACTION, NEW_ACTION)
            p.write_text(text, encoding="utf-8")
            print(f"✅ Đã chuẩn hoá nội dung export/import n8n trong {p.name}")
        else:
            print(f"Không tìm thấy chuỗi cũ trong {p.name}")

if __name__ == "__main__":
    update()
