# -*- coding: utf-8 -*-
"""
Layout Validator: Kiểm tra tính chuẩn mực của mã HTML in ấn A4.
"""
import re
from typing import List
from ..schemas import Violation

class LayoutValidator:
    def check(self, html_content: str) -> List[Violation]:
        violations = []

        # 1. Kiểm tra font Montserrat
        if "Montserrat" not in html_content:
            violations.append(Violation(
                gate_name="LayoutGate",
                severity="CRITICAL",
                location="<head>",
                message="File HTML thiếu font chữ tiêu chuẩn 'Montserrat' của Công ty Kiên Thành Tín!",
                expected="font-family: 'Montserrat', sans-serif",
                actual="Không tìm thấy font Montserrat",
                suggested_fix="Bổ sung Google Fonts link Montserrat vào <head>"
            ))

        # 2. Kiểm tra CSS @page A4
        if "@page" not in html_content or "A4" not in html_content:
            violations.append(Violation(
                gate_name="LayoutGate",
                severity="WARNING",
                location="<style>",
                message="Thiếu quy chuẩn in ấn @page A4 portrait.",
                expected="@page { size: A4 portrait; }",
                actual="Thiếu @page",
                suggested_fix="Bổ sung cấu hình CSS in ấn A4"
            ))

        # 3. Kiểm tra tính cân đối của các thẻ HTML cơ bản
        tags_to_check = ["div", "table", "tr", "th", "td", "ul", "li"]
        for tag in tags_to_check:
            open_count = len(re.findall(rf"<{tag}\b", html_content, re.IGNORECASE))
            close_count = len(re.findall(rf"</{tag}>", html_content, re.IGNORECASE))
            if open_count != close_count:
                violations.append(Violation(
                    gate_name="LayoutGate",
                    severity="CRITICAL",
                    location=f"<{tag}>",
                    message=f"Thẻ <{tag}> không cân bằng: {open_count} mở vs {close_count} đóng. Nguy cơ vỡ layout khi in!",
                    expected=f"Số thẻ mở bằng số thẻ đóng ({open_count})",
                    actual=f"Mở: {open_count}, Đóng: {close_count}",
                    suggested_fix=f"Đóng đầy đủ các thẻ <{tag}>"
                ))

        return violations
