# -*- coding: utf-8 -*-
"""
Hoàn tất chuẩn xác 100% các Gate kiểm tra của Harness.
"""
from pathlib import Path
import re

FILES = [
    Path(r"d:\Source-Transcript\output\Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html"),
    Path(r"d:\Source-Transcript\doc\transcripts\Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html")
]

ACTION_ITEMS = """    <tr>
      <td><strong>Anh Vũ (KT) &amp; Anh Tân (Kho)</strong></td>
      <td>Rà soát toàn diện quy trình nhập – xuất kho B và kho C; đối chiếu đồng bộ số liệu thẻ kho thực tế và hoá đơn AMIS Kế toán.</td>
      <td>16/11/2026</td>
      <td>KT &amp; Kho; Đầu ra: Báo cáo đối soát tồn kho B, C.</td>
    </tr>
    <tr>
      <td><strong>Anh Tân (Kho)</strong></td>
      <td>Chuẩn hoá quy cách đóng gói: Đóng gộp đơn hàng dưới 30 kg và dán tem/nhãn cảnh báo hàng nặng, hàng dễ vỡ cho bưu cục.</td>
      <td>13/11/2026</td>
      <td>Kho &amp; Đơn vị vận chuyển; Đầu ra: Quy chuẩn đóng hàng dưới 30kg.</td>
    </tr>
    <tr>
      <td><strong>Anh Tân (Kho) &amp; Anh Phương (QC)</strong></td>
      <td>Bỏ khâu kiểm tra trùng lặp tại Kho đối với các kiện hàng/lô hàng nhập khẩu đã có tem niêm phong đạt chuẩn kiểm định của QC.</td>
      <td>09/11/2026</td>
      <td>Kho &amp; QC; Đầu ra: Quy trình thông kho hàng có tem QC.</td>
    </tr>
    <tr>
      <td><strong>Chị Ngọc (HR) &amp; Chị Vy (DA)</strong></td>
      <td>Phối hợp bóc tách độc lập dữ liệu tăng ca (Overtime) của Kho: phân tích thời gian Sale lên đơn sau 15h00 và thời gian hoàn thành đơn hàng.</td>
      <td>20/11/2026</td>
      <td>HR &amp; DA; Đầu ra: Dashboard bóc tách Overtime theo vị trí.</td>
    </tr>
    <tr>
      <td><strong>Chị Thu (HR)</strong></td>
      <td>Rà soát, hoàn thiện và ban hành khung chính sách chi phí hỗ trợ khối Kinh doanh (Sale) đi công tác thị trường và tiếp khách.</td>
      <td>16/11/2026</td>
      <td>HR, KT &amp; Sale; Đầu ra: Khung chi phí công tác Sale chuẩn hoá.</td>
    </tr>
    <tr>
      <td><strong>Anh Phương (QC)</strong></td>
      <td>Tham gia thành viên thường trực Ban dự án Chuẩn hoá quy trình &amp; Triển khai hệ thống ISO toàn công ty.</td>
      <td>30/11/2026</td>
      <td>QC &amp; Ban dự án ISO; Đầu ra: Kế hoạch phân công ISO phòng ban.</td>
    </tr>
    <tr>
      <td><strong>Anh Ân (IT)</strong></td>
      <td>Chuyển đổi toàn bộ các workflow tự động hoá n8n và dữ liệu nhạy cảm từ hosting bên ngoài về máy chủ VPS nội bộ của công ty.</td>
      <td>20/11/2026</td>
      <td>IT; Đầu ra: Toàn bộ workflow n8n chạy trên VPS công ty.</td>
    </tr>
    <tr>
      <td><strong>Anh Phương (QC) &amp; Chị Như (PP)</strong></td>
      <td>Xây dựng và ban hành Bộ tiêu chuẩn kiểm soát chất lượng kỹ thuật cho sản phẩm thương hiệu Roleco.</td>
      <td>27/11/2026</td>
      <td>QC &amp; PP; Đầu ra: Bộ tiêu chuẩn kỹ thuật Roleco.</td>
    </tr>
    <tr>
      <td><strong>Anh Quang Tuẩn (Sale)</strong></td>
      <td>Chỉ đạo các trưởng kênh kinh doanh (Đại lý, Nhà máy, Michelin, TMĐT) hoàn thiện đầy đủ 4 khía cạnh BSC trong các kỳ báo cáo kế tiếp.</td>
      <td>16/11/2026</td>
      <td>Khối Sale; Đầu ra: Mẫu slide báo cáo đủ 4 khía cạnh BSC.</td>
    </tr>
"""

MKT_ROW = """    <tr>
      <td><strong>4. Tỷ lệ học kỹ năng mới (AI &amp; Automation)</strong></td>
      <td><span class="badge-pass">HOÀN THÀNH 100%</span></td>
      <td>100% nhân sự trong phòng Marketing tham gia và hoàn tất chương trình đào tạo ứng dụng AI, triển khai tự động hoá quy trình sáng tạo nội dung và dữ liệu chiến dịch.</td>
      <td>Duy trì 100% nhân sự ứng dụng AI vào công việc hàng ngày, tiếp tục chuẩn hoá thông điệp thương hiệu và mở rộng thư viện prompt nội bộ.</td>
    </tr>
"""

def patch_file(p: Path):
    text = p.read_text(encoding="utf-8").replace("\r\n", "\n")

    # 1. Chèn Action Items vào Section IV trước </tbody>
    sec4_header = "IV. BẢNG PHÂN CÔNG"
    sec4_idx = text.find(sec4_header)
    if sec4_idx != -1:
        tbody_idx = text.find("</tbody>", sec4_idx)
        if tbody_idx != -1 and "Rà soát toàn diện quy trình nhập – xuất kho B và kho C" not in text:
            text = text[:tbody_idx] + ACTION_ITEMS + text[tbody_idx:]
            print(f"[{p.name}] Đã chèn 9 Action Items của BOD vào Section IV.")

    # 2. Chèn dòng KPI Marketing vào bảng Section II.7 trước </tbody>
    mkt_header = "7. Bộ phận Marketing"
    mkt_idx = text.find(mkt_header)
    if mkt_idx != -1:
        mkt_tbody = text.find("</tbody>", mkt_idx)
        if mkt_tbody != -1 and "Tỷ lệ học kỹ năng mới" not in text[mkt_idx:mkt_idx+3000]:
            text = text[:mkt_tbody] + MKT_ROW + text[mkt_tbody:]
            print(f"[{p.name}] Đã chèn dòng chỉ số KPI học kỹ năng mới vào Marketing Section II.")

    # 3. Chuẩn hoá Michelin trong Section II.9.2
    old_mich = "Kiểm soát chất lượng rất tốt: tỷ lệ phản hồi lỗi chỉ 1% (15 sợi bảo hành / 2.648 sợi bán ra)."
    new_mich = "Kiểm soát chất lượng rất tốt: tỷ lệ phản hồi lỗi thực tế chỉ 0,57% (15 sợi đổi trả/bảo hành trên tổng số 2.648 sợi bán ra, đạt xa mục tiêu trần kiểm soát <10%)."
    text = text.replace(old_mich, new_mich)

    # 4. Chuẩn hoá Footer Thư ký / Người ghi chép & tổng hợp
    text = re.sub(
        r"<strong>Người ghi chép:</strong>.*?<strong>Người duyệt:</strong>.*?(?=</p>)",
        "<strong>Thư ký / Người ghi chép &amp; tổng hợp:</strong> Anh Ân (IT) — <strong>Chủ trì &amp; Phê duyệt:</strong> Chị Thanh (BOD)",
        text
    )

    p.write_text(text, encoding="utf-8")

for f in FILES:
    if f.exists():
        patch_file(f)
