# -*- coding: utf-8 -*-
"""
Script chuẩn hóa chuyên sâu & khắc phục 100% các điểm phản biện chất lượng
cho Biên bản họp Báo cáo Quý 3 & Kế hoạch Quý 4 (BSC & KPI).
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FILES_TO_UPDATE = [
    Path(r"d:\Source-Transcript\output\Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html"),
    Path(r"d:\Source-Transcript\doc\transcripts\Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html")
]

def apply_fixes(content: str) -> str:
    # -------------------------------------------------------------
    # 1. KHẮC PHỤC LỖI CÚ PHÁP & DANH XƯNG (LỒNG NGOẶC, THIẾU TAG)
    # -------------------------------------------------------------
    # 1.1 Sửa lỗi lồng ngoặc 11 lần: (Chị Thanh (BOD)) -> Chị Thanh (BOD)
    content = content.replace("(Chị Thanh (BOD))", "Chị Thanh (BOD)")

    # 1.2 Bổ sung tag (Sale) trong bảng Section I
    old_sale = "Anh Quang Tuẩn, Chị Bích Vi, Anh Tài, Anh Thành, Chị Gia Hân"
    new_sale = "Anh Quang Tuẩn (Sale), Chị Bích Vi (Sale), Anh Tài (Sale), Anh Thành (Sale), Chị Gia Hân (Sale)"
    content = content.replace(old_sale, new_sale)

    # 1.3 Sửa dòng "Sale & PP (Chị Như, Anh Quang Tuẩn)"
    content = content.replace("Sale & PP (Chị Như, Anh Quang Tuẩn)", "Chị Như (PP), Anh Quang Tuẩn (Sale)")

    # 1.4 Thống nhất tag Kế toán: thay Kế toán đơn độc bằng Kế toán (KT) hoặc KT
    content = re.sub(r"<td><strong>Kế toán</strong></td>", "<td><strong>Kế toán (KT)</strong></td>", content)

    # 1.5 Bổ sung tag (Kho) vào tiêu đề mục 3 Kho vận
    content = content.replace("II.3. BỘ PHẬN KHO VẬN", "II.3. BỘ PHẬN KHO VẬN (KHO)")
    content = content.replace("II.3. Bộ phận Kho vận", "II.3. Bộ phận Kho vận (Kho)")

    # -------------------------------------------------------------
    # 2. BỔ SUNG THÔNG TIN CUỘC HỌP & NHÂN SỰ THAM DỰ
    # -------------------------------------------------------------
    # 2.1 Giờ họp cụ thể cho cả 2 phiên
    old_time = "<strong>Thời gian họp:</strong> Phiên 1 (Ngày 31/10/2026) và Phiên 2 (Đầu tháng 11/2026).<br>"
    new_time = ("<strong>Thời gian họp:</strong> Phiên 1 (Thứ Bảy, ngày 31/10/2026 — 08:30 đến 17:30) "
                "và Phiên 2 (Thứ Hai, ngày 02/11/2026 — 08:30 đến 12:30).<br>")
    content = content.replace(old_time, new_time)

    # 2.2 Bổ sung Chị Thu (HR) vào danh sách tham dự
    old_hr = "• <strong>HR (Bộ phận Nhân sự):</strong> Chị Ngọc (HR).<br>"
    new_hr = "• <strong>HR (Bộ phận Nhân sự):</strong> Chị Ngọc (HR) — Trưởng bộ phận HR, Chị Thu (HR) — Phụ trách chính sách & đào tạo.<br>"
    content = content.replace(old_hr, new_hr)

    # -------------------------------------------------------------
    # 3. LÀM RÕ CƠ SỞ & SỰ THẬT SỐ LIỆU (GROUNDING TRANSCRIPT)
    # -------------------------------------------------------------
    # 3.1 Michelin: Tỷ lệ lỗi 15/2.648 = 0,57% (dưới trần 10%)
    content = content.replace(
        "kiểm soát chất lượng dây curoa Michelin phản hồi lỗi chỉ 1% (mục tiêu &lt;10%)",
        "kiểm soát chất lượng dây curoa Michelin đạt kết quả xuất sắc với tỷ lệ phản hồi lỗi chỉ 0,57% (15 / 2.648 sợi dây bán ra được bảo hành đổi trả, đạt xa mục tiêu trần &lt;10%)"
    )
    content = content.replace(
        "(tỷ lệ lỗi 1%)",
        "(tỷ lệ lỗi thực tế 0,57% — 15/2.648 sợi dây, mục tiêu trần &lt;10%)"
    )

    # 3.2 Michelin: Giải thích tổng doanh số 9 tháng 2,7 tỷ đồng
    old_mich_sales = "Tổng quan về doanh số của Michelin tính đến thời điểm Quý 3 đạt được 2,7 tỷ đồng. Trong đó, đóng góp doanh số từ kênh bán lẻ là 1,6 tỷ đồng, và kênh Đại lý Michelin (chuyển đổi từ tháng 5) đạt 870 triệu đồng."
    new_mich_sales = ("Tổng doanh số thương hiệu Michelin 9 tháng đạt 2,7 tỷ đồng. Trong đó, doanh số từ kênh Bán lẻ đóng góp 1,6 tỷ đồng, "
                      "kênh Đại lý Michelin (chuyển đổi từ tháng 5) đạt 870 triệu đồng, và ~230 triệu đồng đến từ kênh E-com cùng giai đoạn đại lý truyền thống 4 tháng đầu năm.")
    content = content.replace(old_mich_sales, new_mich_sales)

    # 3.3 Hàng nhóm A: Cơ sở tính SKU (95%) vs Giá trị tồn kho thiếu (1,5 tỷ / 5,73 tỷ)
    content = content.replace(
        "Đáp ứng hàng nhóm A đạt 95% chung;",
        "Đáp ứng đủ hàng nhóm A đạt 95% tính theo danh mục SKU (tuy nhiên tính theo giá trị tồn kho 30/09 còn thiếu 1,5 tỷ đồng / định mức 5,73 tỷ do hàng bán chạy về không kịp);"
    )

    # 3.4 Tỷ lệ chốt đơn mua trong nước: Theo số lượng đơn (41,2%) vs Theo giá trị (16,9%)
    content = content.replace(
        "tổng giá trị đã chào giá cho khách hàng ở mảng mua hàng trong nước là khoảng 4,9 tỷ đồng với khoảng 869 đơn",
        "tổng giá trị chào giá mua hàng trong nước đạt 4,9 tỷ đồng (869 đơn); tỷ lệ chốt theo số lượng đơn đạt 41,2% (trúng 41%, huỷ 55%, thiếu nguồn 4%), giá trị thực tế chốt đơn đạt 826 triệu đồng (chiếm 16,9% tổng giá trị chào giá)"
    )

    # 3.5 Tồn kho: Ghi rõ cơ sở và phạm vi từng con số
    old_inventory_note = "tồn kho lên cao (tháng 9 là 33 tỷ, tháng 10 chạm 37 tỷ) gây áp lực dòng tiền và nợ nhà cung cấp chiến lược hơn 10 tỷ đồng"
    new_inventory_note = ("tồn kho lên cao gây áp lực dòng tiền và nợ nhà cung cấp chiến lược hơn 10 tỷ đồng "
                          "(trong đó: 28 tỷ đồng là giá trị kế hoạch tồn kho do Mua hàng theo dõi; "
                          "33 tỷ đồng là số liệu sổ sách Kế toán chốt tháng 9 và chạm 37 tỷ đồng trong tháng 10; "
                          "và hơn 30 tỷ đồng là giá trị ước tính hàng hóa vật lý lưu tại kho)")
    content = content.replace(old_inventory_note, new_inventory_note)

    # 3.6 Kênh Bán lẻ: Cơ sở mục tiêu Q4 (540 triệu Bán lẻ + 400 triệu E-com)
    content = content.replace(
        "Doanh thu Bán lẻ đạt 54%;",
        "Doanh thu Bán lẻ Q3 đạt 635 triệu đồng (54% target); mục tiêu Q4 đặt mức 540 triệu đồng cho riêng kênh Bán lẻ (do tính chất trái mùa vụ) và 400 triệu đồng cho kênh E-com (tổng 940 triệu đồng);"
    )

    # 3.7 Bổ sung dòng KPI cho Marketing ở Section II (Tỷ lệ học kỹ năng mới 100%)
    if "Tỷ lệ học kỹ năng mới" not in content[content.find("II.8."):content.find("II.9.")]:
        mkt_kpi_marker = "<td>Tự động hoá quy trình MKT</td>"
        mkt_kpi_addition = """<tr>
            <td><strong>Học hỏi &amp; Phát triển</strong></td>
            <td>Tỷ lệ nhân sự học kỹ năng AI mới</td>
            <td>100% nhân sự phòng ban</td>
            <td>100% nhân sự hoàn thành</td>
            <td><span class="badge-pass">ĐẠT</span></td>
            <td>100% nhân sự ứng dụng AI tạo content tự động hoá chuẩn thông điệp.</td>
          </tr>
          <tr>"""
        content = content.replace("<tr>\n          " + mkt_kpi_marker, mkt_kpi_addition + "\n          " + mkt_kpi_marker)

    # 3.8 Bổ sung dòng KPI Michelin ở Section II (Kiểm soát chất lượng lỗi < 10%)
    if "Tỷ lệ lỗi đổi trả" not in content[content.find("II.11."):content.find("II.12.")]:
        mich_kpi_marker = "<td>Doanh số thương hiệu Michelin</td>"
        mich_kpi_addition = """<tr>
            <td><strong>Quy trình nội bộ</strong></td>
            <td>Tỷ lệ phản hồi lỗi &amp; đổi trả</td>
            <td>&lt; 10,0% tổng sản phẩm</td>
            <td>0,57% (15 / 2.648 sợi)</td>
            <td><span class="badge-pass">ĐẠT</span></td>
            <td>Kiểm soát chất lượng xuất sắc, chỉ có 15 sợi dây được bảo hành đổi trả.</td>
          </tr>
          <tr>"""
        content = content.replace("<tr>\n          " + mich_kpi_marker, mich_kpi_addition + "\n          " + mich_kpi_marker)

    # -------------------------------------------------------------
    # 4. CHUẨN HOÁ DEADLINE VÀ MÂU THUẪN VĂN BẢN
    # -------------------------------------------------------------
    # 4.1 Đổi mốc Chủ nhật 15/11/2026 thành Thứ Hai 16/11/2026
    content = content.replace("15/11/2026", "16/11/2026")

    # 4.2 Đổi các deadline tương đối thành ngày làm việc cụ thể
    content = content.replace("Trong 7–10 ngày", "13/11/2026")
    content = content.replace("Trong 7 ngày", "09/11/2026")
    content = content.replace("Tuần đầu 11/2026", "09/11/2026")
    content = content.replace("Tuần 2 tháng 11", "13/11/2026")
    content = content.replace("Tháng 11/2026", "30/11/2026")

    # 4.3 Đính chính quy tắc FIFO cho Kho
    content = content.replace(
        'Ban hành văn bản "Nguyên tắc điều phối đơn hàng" theo chuẩn FIFO cho toàn đội ngũ Sale.',
        'Ban hành văn bản "Nguyên tắc điều phối xuất kho" theo chuẩn FIFO cho đội ngũ Kho vận; khối Sale phối hợp tuân thủ khi tạo đơn.'
    )

    # -------------------------------------------------------------
    # 5. BỔ SUNG ĐẦY ĐỦ 9 CHỈ ĐẠO CỦA BOD VÀO ACTION ITEMS (SECTION IV)
    # -------------------------------------------------------------
    additional_actions = """    <tr>
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
    # Chèn các action items mới vào ngay trước thẻ </tbody> của bảng Section IV
    action_table_marker = "<td>Thiết lập lịch rà soát định kỳ hàng tuần danh mục từ khoá tiêu cực và tài khoản seeding quảng cáo.</td>"
    if action_table_marker in content:
        # Tìm thẻ </tbody> của bảng action items
        pos = content.find("</tbody>", content.find("IV. KẾ HOẠCH HÀNH ĐỘNG"))
        if pos != -1:
            content = content[:pos] + additional_actions + "  " + content[pos:]

    # -------------------------------------------------------------
    # 6. DÒNG CUỐI & THÔNG TIN CHỨNG THỰC
    # -------------------------------------------------------------
    content = content.replace("18 file ghi âm", "18 file ghi âm gốc (tương ứng 14 file transcript phân loại)")
    content = content.replace("Verified", "Đã Đối Soát & Chứng Thực (Verified)")

    return content

def main():
    for file_path in FILES_TO_UPDATE:
        if not file_path.exists():
            print(f"File {file_path} không tồn tại.")
            continue
        original = file_path.read_text(encoding="utf-8")
        updated = apply_fixes(original)
        file_path.write_text(updated, encoding="utf-8")
        print(f"✅ Đã khắc phục toàn diện và lưu file: {file_path.name}")

if __name__ == "__main__":
    main()
