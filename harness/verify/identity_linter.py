# -*- coding: utf-8 -*-
"""
Identity & Gender Linter: Chốt kiểm soát danh xưng, giới tính & tag bộ phận (Anti-Misgendering).
"""
import re
import unicodedata
from typing import List
from ..schemas import MeetingAST, Violation
from ..gather.knowledge_registry import KnowledgeRegistry

class IdentityLinter:
    def __init__(self, registry: KnowledgeRegistry):
        self.registry = registry

    def check(self, ast: MeetingAST) -> List[Violation]:
        violations = []

        # 1. Kiểm tra danh sách người tham dự
        for att in ast.attendees:
            registered = self.registry.resolve_person(att.name)
            if registered:
                if att.gender_pronoun != registered["gender"]:
                    violations.append(Violation(
                        gate_name="IdentityGate",
                        severity="CRITICAL",
                        location=f"Attendee: {att.full_display}",
                        message=f"Sai giới tính nhân sự! '{att.name}' là '{registered['gender']}', không phải '{att.gender_pronoun}'.",
                        expected=registered["gender"],
                        actual=att.gender_pronoun,
                        suggested_fix=f"Sửa thành '{registered['full']}'"
                    ))

        # 2. Kiểm tra danh xưng trong Action Items
        person_tag_pattern = re.compile(r"^(Anh|Chị)\s+([^(]+)\s*\(([^)]+)\)$")
        for act in ast.action_items:
            pic = act.pic.strip()
            match = person_tag_pattern.match(pic)
            if not match:
                violations.append(Violation(
                    gate_name="IdentityGate",
                    severity="WARNING",
                    location=f"ActionItem {act.item_id}",
                    message=f"Người phụ trách '{pic}' chưa đúng định dạng '<Anh/Chị> <Tên> (<Tag Bộ phận>)'",
                    expected="<Anh/Chị> <Tên> (<Tag>)",
                    actual=pic,
                    suggested_fix="Bổ sung danh xưng và tag bộ phận chuẩn"
                ))
            else:
                gender, name = match.group(1), match.group(2).strip()
                registered = self.registry.resolve_person(name)
                if registered and registered["gender"] != gender:
                    violations.append(Violation(
                        gate_name="IdentityGate",
                        severity="CRITICAL",
                        location=f"ActionItem {act.item_id}",
                        message=f"Sai giới tính người phụ trách! '{name}' là '{registered['gender']}'.",
                        expected=registered["gender"],
                        actual=gender,
                        suggested_fix=f"Sửa PIC thành '{registered['full']}'"
                    ))

        return violations
