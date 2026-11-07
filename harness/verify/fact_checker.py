# -*- coding: utf-8 -*-
"""
Fact Checker: Chốt kiểm soát Bảo toàn Sự thật (Zero-Hallucination Gate).
Kiểm tra đối chiếu 100% số liệu, %, tiền tệ và deadline với bản ghi âm/transcript gốc.
"""
import re
import unicodedata
from typing import List, Tuple
from ..schemas import MeetingAST, Violation

class FactChecker:
    def __init__(self, raw_transcript: str):
        self.raw_transcript = unicodedata.normalize("NFC", raw_transcript.lower())

    def check(self, ast: MeetingAST) -> List[Violation]:
        violations = []

        # 1. Quét đối chiếu số liệu trong báo cáo KPI
        for idx, kpi in enumerate(ast.kpi_reports, start=1):
            numbers = re.findall(r"\d+(?:[.,]\d+)?", kpi.actual)
            for num in numbers:
                # Nếu con số không hề xuất hiện trong transcript gốc
                if num not in self.raw_transcript:
                    violations.append(Violation(
                        gate_name="ZeroHallucinationGate",
                        severity="CRITICAL",
                        location=f"KPI Report #{idx} ({kpi.department})",
                        message=f"Số liệu '{num}' không tìm thấy trong transcript gốc. Nghi vấn ảo giác!",
                        expected="Số liệu phải có căn cứ từ audio/transcript",
                        actual=kpi.actual,
                        suggested_fix=f"Gắn thẻ [cần kiểm tra lại số liệu: {num}] hoặc loại bỏ"
                    ))

        # 2. Quét đối chiếu hạn hoàn thành (Deadline) trong Action Items
        for act in ast.action_items:
            if act.deadline and act.deadline != "Chưa xác định":
                clean_deadline = act.deadline.lower()
                # Kiểm tra xem từ khóa deadline có xuất hiện trong transcript không
                deadline_tokens = [tok for tok in clean_deadline.split() if len(tok) > 2]
                matched = any(tok in self.raw_transcript for tok in deadline_tokens)

                if not matched:
                    violations.append(Violation(
                        gate_name="ZeroHallucinationGate",
                        severity="CRITICAL",
                        location=f"ActionItem {act.item_id} ({act.pic})",
                        message=f"Hạn hoàn thành '{act.deadline}' không được người nói chốt trong cuộc họp!",
                        expected="Deadline phải được phát biểu rõ, nếu không bắt buộc ghi 'Chưa xác định'",
                        actual=act.deadline,
                        suggested_fix="Chuyển hạn chót thành 'Chưa xác định' và đưa vào danh sách cần bổ sung"
                    ))

        return violations
