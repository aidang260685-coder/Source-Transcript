# -*- coding: utf-8 -*-
"""
HTML Meeting Renderer: Biên dịch Meeting AST thành văn bản HTML chuẩn in A4 (Kiên Thành Tín).
Tuân thủ 100% Montserrat font, bảng biểu chuẩn mực, có letterhead và khu vực ký tên.
"""
import html
from typing import Optional
from ..schemas import MeetingAST

class HTMLMeetingRenderer:
    @staticmethod
    def render(ast: MeetingAST) -> str:
        """Biên dịch đối tượng AST sang mã HTML hoàn chỉnh"""

        # Danh sách người tham dự
        attendee_badges = "".join([
            f'<span class="badge">{html.escape(att.full_display)}</span> '
            for att in ast.attendees
        ]) if ast.attendees else '<em>Chưa ghi nhận đầy đủ</em>'

        # Bảng KPI & Báo cáo Vận hành
        kpi_rows = ""
        if ast.kpi_reports:
            for idx, kpi in enumerate(ast.kpi_reports[:15], start=1):  # Giới hạn hiển thị 15 dòng nổi bật
                kpi_rows += f"""
                <tr>
                    <td style="text-align:center;">{idx}</td>
                    <td><strong>{html.escape(kpi.department)}</strong></td>
                    <td>{html.escape(kpi.actual)}</td>
                    <td style="text-align:center;"><span class="status-tag status-done">{html.escape(kpi.status)}</span></td>
                </tr>
                """
        else:
            kpi_rows = '<tr><td colspan="4" style="text-align:center;"><em>Không có chỉ số phát sinh</em></td></tr>'

        # Đánh giá của Ban Giám đốc (BOD)
        bod_content = ""
        if ast.bod_evaluations:
            for bod in ast.bod_evaluations:
                directives_list = "".join([f"<li>{html.escape(d)}</li>" for d in bod.directives])
                bod_content += f"""
                <div class="bod-box">
                    <h4 style="color:#004085; margin-bottom:6px;">👤 {html.escape(bod.leader)}</h4>
                    <ul>{directives_list}</ul>
                </div>
                """
        else:
            bod_content = '<p><em>Ban Giám đốc ghi nhận báo cáo và sẽ có chỉ đạo cụ thể bằng văn bản.</em></p>'

        # Bảng Action Items (Phân công công việc)
        action_rows = ""
        if ast.action_items:
            for act in ast.action_items:
                deadline_style = 'color: #721c24; font-weight: 600;' if act.deadline == "Chưa xác định" else 'color: #155724; font-weight: 600;'
                action_rows += f"""
                <tr>
                    <td style="text-align:center; font-weight:bold;">{html.escape(act.item_id)}</td>
                    <td>{html.escape(act.task)}</td>
                    <td><strong>{html.escape(act.pic)}</strong></td>
                    <td style="text-align:center; {deadline_style}">{html.escape(act.deadline)}</td>
                </tr>
                """
        else:
            action_rows = '<tr><td colspan="4" style="text-align:center;"><em>Không có nhiệm vụ phát sinh ngoài kế hoạch</em></td></tr>'

        # Danh sách đoạn âm thanh [??] cần kiểm tra
        flagged_content = ""
        if ast.flagged_segments:
            flagged_items = "".join([
                f'<li><strong>{html.escape(f.timestamp)}</strong>: <code>{html.escape(f.raw_text)}</code></li>'
                for f in ast.flagged_segments
            ])
            flagged_content = f"""
            <div class="flagged-box">
                <h4 style="color:#721c24; margin-top:0;">⚠️ CÁC ĐOẠN ÂM THANH CẦN KIỂM TRA LẠI (ĐỘ TIN CẬY THẤP)</h4>
                <ul>{flagged_items}</ul>
            </div>
            """

        html_doc = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(ast.title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: A4 portrait;
            margin: 20mm 15mm 20mm 15mm;
        }}
        * {{
            box-sizing: border-box;
            font-family: 'Montserrat', sans-serif;
        }}
        body {{
            margin: 0;
            padding: 24px;
            color: #212529;
            background-color: #f8f9fa;
            font-size: 13.5px;
            line-height: 1.6;
        }}
        .page-container {{
            max-width: 210mm;
            margin: 0 auto;
            background: #ffffff;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-radius: 4px;
        }}
        .header {{
            border-bottom: 2px solid #003366;
            padding-bottom: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .company-name {{
            font-size: 16px;
            font-weight: 700;
            color: #003366;
            text-transform: uppercase;
        }}
        .company-sub {{
            font-size: 11px;
            color: #6c757d;
        }}
        .doc-title {{
            text-align: center;
            font-size: 18px;
            font-weight: 700;
            color: #003366;
            text-transform: uppercase;
            margin: 20px 0;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 16px;
            background: #f1f5f9;
            padding: 14px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: 700;
            color: #003366;
            text-transform: uppercase;
            border-left: 4px solid #003366;
            padding-left: 8px;
            margin: 24px 0 12px 0;
        }}
        .badge {{
            display: inline-block;
            background: #e2e8f0;
            color: #1e293b;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-bottom: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
        }}
        th, td {{
            border: 1px solid #cbd5e1;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background: #f8fafc;
            color: #003366;
            font-weight: 600;
            font-size: 12.5px;
        }}
        .status-tag {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .status-done {{
            background: #d4edda;
            color: #155724;
        }}
        .bod-box {{
            background: #eef6ff;
            border-left: 4px solid #0066cc;
            padding: 12px 16px;
            margin-bottom: 12px;
            border-radius: 0 6px 6px 0;
        }}
        .flagged-box {{
            background: #fff3cd;
            border: 1px solid #ffeeba;
            color: #856404;
            padding: 12px 16px;
            border-radius: 6px;
            margin-top: 24px;
        }}
        .signature-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            text-align: center;
            margin-top: 40px;
            page-break-inside: avoid;
        }}
        .sign-title {{
            font-weight: 700;
            color: #003366;
            margin-bottom: 60px;
        }}
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .page-container {{
                box-shadow: none;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="page-container">
        <!-- Letterhead -->
        <div class="header">
            <div>
                <div class="company-name">CÔNG TY TNHH KIÊN THÀNH TÍN</div>
                <div class="company-sub">Hệ Thống Quản Trị & Vận Hành Vòng Bi - Phụ Tùng</div>
            </div>
            <div style="text-align: right; font-size: 11px; color: #6c757d;">
                <div>Hệ Thống Tự Trị Harness 2026</div>
                <div>Trạng thái: Đã Xác Minh Sự Thật</div>
            </div>
        </div>

        <!-- Tiêu đề -->
        <div class="doc-title">{html.escape(ast.title)}</div>

        <!-- Meta Grid -->
        <div class="meta-grid">
            <div><strong>📅 Thời gian:</strong> {html.escape(ast.date)}</div>
            <div><strong>📍 Địa điểm:</strong> {html.escape(ast.location)}</div>
            <div><strong>👤 Chủ trì:</strong> {html.escape(ast.chairperson)}</div>
            <div><strong>📝 Thư ký:</strong> {html.escape(ast.secretary)}</div>
        </div>

        <!-- I. Thành phần tham dự -->
        <div class="section-title">I. THÀNH PHẦN THAM DỰ</div>
        <div style="margin-bottom: 16px;">
            {attendee_badges}
        </div>

        <!-- II. Báo cáo & Số liệu vận hành -->
        <div class="section-title">II. NỘI DUNG BÁO CÁO & CHỈ SỐ VẬN HÀNH</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 5%; text-align:center;">STT</th>
                    <th style="width: 20%;">Bộ phận</th>
                    <th>Nội dung chỉ số / Số liệu ghi nhận</th>
                    <th style="width: 15%; text-align:center;">Tình trạng</th>
                </tr>
            </thead>
            <tbody>
                {kpi_rows}
            </tbody>
        </table>

        <!-- III. Đánh giá của Ban Giám Đốc -->
        <div class="section-title">III. KẾT LUẬN & CHỈ ĐẠO CỦA BAN GIÁM ĐỐC (BOD)</div>
        {bod_content}

        <!-- IV. Phân công công việc (Action Items) -->
        <div class="section-title">IV. PHÂN CÔNG THỰC HIỆN & THỜI HẠN (ACTION ITEMS)</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 10%; text-align:center;">Mã</th>
                    <th>Nội dung công việc</th>
                    <th style="width: 25%;">Nhân sự phụ trách (PIC)</th>
                    <th style="width: 18%; text-align:center;">Thời hạn</th>
                </tr>
            </thead>
            <tbody>
                {action_rows}
            </tbody>
        </table>

        <!-- V. Các đoạn âm thanh cần kiểm tra -->
        {flagged_content}

        <!-- Khu vực ký tên -->
        <div class="signature-grid">
            <div>
                <div class="sign-title">ĐẠI DIỆN THƯ KÝ CUỘC HỌP</div>
                <div><em>(Ký & ghi rõ họ tên)</em></div>
            </div>
            <div>
                <div class="sign-title">CHỦ TRÌ CUỘC HỌP (BOD)</div>
                <div><em>(Ký & ghi rõ họ tên)</em></div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_doc
