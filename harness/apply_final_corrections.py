from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
# -*- coding: utf-8 -*-
"""
Hoàn thiện toàn bộ các điểm phản biện chất lượng và chuẩn hoá vai trò Thư ký / Người ghi chép.
"""
from pathlib import Path
import re

FILES = [
    BASE_DIR / "output" / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html",
    BASE_DIR / "doc" / "transcripts" / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html"
]

def update_file(p: Path):
    text = p.read_text(encoding="utf-8")

    # 1. Chuẩn hoá Footer: Thư ký / Người ghi chép & tổng hợp: Anh Ân (IT) — Chủ trì & Phê duyệt: Chị Thanh (BOD)
    text = re.sub(
        r"<strong>Người ghi chép:</strong>.*?<strong>Người duyệt:</strong>.*?(?=</p>)",
        "<strong>Thư ký / Người ghi chép &amp; tổng hợp:</strong> Anh Ân (IT) — <strong>Chủ trì &amp; Phê duyệt:</strong> Chị Thanh (BOD)",
        text
    )

    # 2. Thêm tag (Kho) cho Subsection 3
    text = text.replace(
        '<div class="subsection-title">3. Bộ phận Kho vận — Người báo cáo: Anh Tân (Kho)</div>',
        '<div class="subsection-title">3. Bộ phận Kho vận (Kho) — Người báo cáo: Anh Tân (Kho)</div>'
    )

    # 3. Chuẩn hoá Mua hàng trong nước: 41,2% theo số đơn vs 16,9% theo giá trị
    text = text.replace(
        "Chào giá 4,9 tỷ (869 đơn, tăng 102%). Doanh thu chốt 826 triệu. Tỷ lệ chốt đơn 41,2%",
        "Chào giá mua trong nước đạt 4,9 tỷ đồng (869 đơn). Tỷ lệ chốt theo số đơn đạt 41,2% (trúng 41%, huỷ 55%, thiếu nguồn 4%); giá trị thực tế chốt đơn đạt 826 triệu đồng / 4,9 tỷ đồng chào giá (tương đương 16,9% theo giá trị)"
    )

    # 4. Thêm dòng KPI "Học kỹ năng mới 100%" vào bảng Marketing ở Section II
    mkt_table_target = "<td>Quý 3 đạt 33 lead (14 đại lý Michelin, 19 truyền thống). Luỹ kế 9 tháng đạt 144 / 113 lead năm. Chi phí lead đại lý cao: 910.000 VNĐ/lead do thu hẹp phạm vi địa lý và nhắm chọn (targeting) chính xác chân dung đại lý.</td>\n      <td>Tối ưu hoá chi phí lead đại lý xuống dưới 750.000 VNĐ/lead trong Quý 4.</td>\n    </tr>"
    mkt_kpi_row = """
    <tr>
      <td><strong>4. Tỷ lệ học kỹ năng mới (AI &amp; Automation)</strong></td>
      <td><span class="badge-pass">HOÀN THÀNH 100%</span></td>
      <td>100% nhân sự trong phòng Marketing tham gia và hoàn tất chương trình đào tạo ứng dụng AI, triển khai tự động hoá quy trình sáng tạo nội dung và dữ liệu chiến dịch.</td>
      <td>Duy trì 100% nhân sự ứng dụng AI vào công việc hàng ngày, tiếp tục chuẩn hoá thông điệp thương hiệu và mở rộng thư viện prompt nội bộ.</td>
    </tr>"""
    if "Tỷ lệ học kỹ năng mới" not in text[text.find("7. Bộ phận Marketing"):text.find("8. Team Dữ liệu")]:
        text = text.replace(mkt_table_target, mkt_table_target + mkt_kpi_row)

    # 5. Cập nhật tỷ lệ lỗi Michelin ở Section II.9.2
    text = text.replace(
        "Kiểm soát chất lượng rất tốt: tỷ lệ phản hồi lỗi chỉ 1% (15 sợi bảo hành / 2.648 sợi bán ra).",
        "Kiểm soát chất lượng rất tốt: tỷ lệ phản hồi lỗi thực tế chỉ 0,57% (15 sợi đổi trả/bảo hành trên tổng số 2.648 sợi bán ra, đạt xa mục tiêu trần kiểm soát &lt;10%)."
    )

    # 6. Bổ sung 9 Action Items của BOD vào bảng Section IV
    action_items_block = """    <tr>
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
    last_action_marker = "<td>Sale, KT, BOD; Đầu ra: Danh sách khách hàng 80/20 &amp; giải pháp nợ.</td>\n    </tr>"
    if "Rà soát toàn diện quy trình nhập – xuất kho B và kho C" not in text:
        text = text.replace(last_action_marker, last_action_marker + "\n" + action_items_block)

    p.write_text(text, encoding="utf-8")
    print(f"✅ Hoàn tất cập nhật: {p.name}")

for f in FILES:
    if f.exists():
        update_file(f)
