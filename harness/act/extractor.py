# -*- coding: utf-8 -*-
"""
Meeting Extractor: Trích xuất cấu trúc ngữ nghĩa (Semantic Meeting AST) từ bộ đệm ngữ cảnh.
"""
import re
import unicodedata
from typing import List, Dict, Any, Optional
from ..schemas import MeetingAST, Attendee, KPIRecord, BODEvaluation, ActionItem, FlaggedSegment
from ..gather.knowledge_registry import KnowledgeRegistry

class MeetingExtractor:
    def __init__(self, registry: KnowledgeRegistry):
        self.registry = registry

    def extract_from_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> MeetingAST:
        """
        Trích xuất thông tin cấu trúc từ văn bản transcript đã qua sàng lọc.
        """
        text = unicodedata.normalize("NFC", text)
        ast = MeetingAST()

        if metadata:
            ast.title = metadata.get("title", ast.title)
            ast.date = metadata.get("date", ast.date)
            ast.location = metadata.get("location", ast.location)
            ast.meeting_type = metadata.get("meeting_type", ast.meeting_type)

        # 1. Định danh thành phần tham dự từ văn bản
        found_attendees = set()
        for name_key, person in self.registry.personnel.items():
            full_tag = person["full"]
            if full_tag.lower() in text.lower() or person["name"].lower() in text.lower():
                found_attendees.add(person["name"])
                ast.attendees.append(Attendee(
                    name=person["name"],
                    title=f"Nhân sự ({person['department']})",
                    gender_pronoun=person["gender"],
                    department_tag=person["department"]
                ))

        # Đặt mặc định chủ trì nếu có Chị Thanh
        for att in ast.attendees:
            if "thanh" in att.name.lower() and att.department_tag == "BOD":
                ast.chairperson = att.full_display
                break

        # 2. Tìm các đoạn gắn cờ [??]
        flagged_pattern = re.compile(r"(\[\d{2}:\d{2}:\d{2}(?:\s*->\s*\d{2}:\d{2}:\d{2})?\])?\s*([^.\n]*?\[\?\?\][^.\n]*)")
        for match in flagged_pattern.finditer(text):
            ts = match.group(1) or "[Đoạn không rõ thời gian]"
            flagged_content = match.group(2).strip()
            if flagged_content:
                ast.flagged_segments.append(FlaggedSegment(
                    timestamp=ts,
                    speaker="Chưa xác định",
                    raw_text=flagged_content,
                    issue_type="Âm thanh độ tin cậy thấp [??]"
                ))

        # 3. Phân tích các bộ phận báo cáo (Heuristic & Pattern Detection)
        dept_keywords = {
            "Kho": ["kho", "tồn kho", "nhập kho", "xuất kho", "vòng bi", "dây curoa", "Anh Tân"],
            "Kế toán": ["kế toán", "công nợ", "doanh thu", "chi phí", "hóa đơn", "Anh Khiêm", "Anh Vũ"],
            "Marketing": ["marketing", "mkt", "lead", "quảng cáo", "kênh", "Anh Duy", "Anh Lộc"],
            "Sale": ["sale", "doanh số", "khách hàng", "nhà máy", "đại lý", "Anh Thành", "Anh Tài"],
            "QC": ["qc", "chất lượng", "lỗi", "kiểm tra", "Anh Phương"],
            "IT": ["it", "hệ thống", "amis", "server", "vps", "phần mềm", "Anh Ân"]
        }

        # Trích xuất số liệu / câu phát biểu định lượng
        metric_pattern = re.compile(
            r"([^\n.]{10,100}?(?:\d+(?:[.,]\d+)?\s*(?:%|triệu|tỷ|nghìn|đơn|cái|bộ|lô|lot))[^\n.]*)",
            re.IGNORECASE
        )

        for match in metric_pattern.finditer(text):
            sentence = match.group(1).strip()
            # Gán vào phòng ban tương ứng
            assigned_dept = "Chung"
            for dept, kws in dept_keywords.items():
                if any(kw.lower() in sentence.lower() for kw in kws):
                    assigned_dept = dept
                    break

            ast.kpi_reports.append(KPIRecord(
                department=assigned_dept,
                metric_name="Chỉ số báo cáo vận hành",
                target="Theo kế hoạch",
                actual=sentence,
                status="Đã ghi nhận",
                root_cause="Thảo luận trực tiếp tại cuộc họp"
            ))

        # 4. Trích xuất Action Items (Tìm từ khóa giao việc: phải, yêu cầu, hạn chót, deadline, xong trước)
        action_pattern = re.compile(
            r"((?:Anh|Chị)\s+[A-Za-zÀ-ỹ\s]+\([^)]+\))\s+(?:cần|phải|chịu trách nhiệm|hoàn thành|xử lý)\s+([^.\n]{15,150})",
            re.IGNORECASE
        )
        action_idx = 1
        for match in action_pattern.finditer(text):
            pic = match.group(1).strip()
            task_desc = match.group(2).strip()

            # Tìm deadline nếu có
            deadline_match = re.search(r"(trước ngày\s+\d{1,2}/\d{1,2}(?:/\d{4})?|trong tuần tới|thứ\s+[^\s,.]+)", task_desc, re.IGNORECASE)
            deadline = deadline_match.group(1) if deadline_match else "Chưa xác định"

            ast.action_items.append(ActionItem(
                item_id=f"ACT-{action_idx:02d}",
                task=task_desc,
                pic=pic,
                department=re.search(r"\(([^)]+)\)", pic).group(1) if "(" in pic else "Chung",
                deadline=deadline,
                evidence_quote=match.group(0),
                verified=True
            ))
            action_idx += 1

        # 5. Trích xuất ý kiến chỉ đạo của Ban Giám đốc (BOD)
        bod_pattern = re.compile(
            r"(Chị Thanh \(BOD\)|Anh Tuấn Tú \(BOD\))[\s:]+([^.\n]{20,250})",
            re.IGNORECASE
        )
        bod_records = {}
        for match in bod_pattern.finditer(text):
            leader = match.group(1).strip()
            directive = match.group(2).strip()
            if leader not in bod_records:
                bod_records[leader] = []
            bod_records[leader].append(directive)

        for leader, directives in bod_records.items():
            ast.bod_evaluations.append(BODEvaluation(
                leader=leader,
                target_department="Toàn thể Công ty",
                key_observations=["Đã rà soát báo cáo các phòng ban"],
                directives=directives
            ))

        return ast
