# -*- coding: utf-8 -*-
"""
Định nghĩa Cấu trúc Dữ liệu Nhận thức (Cognitive Schemas & Meeting AST).
Toàn bộ hệ thống giao tiếp qua các cấu trúc này, không dùng chuỗi văn bản tự do.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
import json

@dataclass
class Attendee:
    name: str                       # Tên riêng (ví dụ: Thanh, Khiêm, Tân)
    title: str                      # Chức vụ
    gender_pronoun: str             # "Anh" hoặc "Chị"
    department_tag: str             # Mã bộ phận: BOD, KT, Kho, MKT, Sale, HR, QC, IT, PP, DA
    confirmed: bool = True          # False nếu chưa chắc chắn giới tính
    full_display: str = ""          # "Chị Thanh (BOD)", "Anh Khiêm (KT)"

    def __post_init__(self):
        if not self.full_display:
            self.full_display = f"{self.gender_pronoun} {self.name} ({self.department_tag})"

@dataclass
class KPIRecord:
    department: str                 # Bộ phận báo cáo
    metric_name: str                # Chỉ số KPI
    target: str                     # Mục tiêu
    actual: str                     # Thực tế đạt được
    variance: str = ""              # Chênh lệch
    status: str = "Đạt"             # "Đạt", "Chưa đạt", "Vượt"
    root_cause: str = ""            # Nguyên nhân phân tích trong cuộc họp

@dataclass
class BODEvaluation:
    leader: str                     # Chị Thanh (BOD) hoặc Anh Tuấn Tú (BOD)
    target_department: str          # Bộ phận nhận chỉ đạo
    key_observations: List[str] = field(default_factory=list)  # Đánh giá sau báo cáo
    directives: List[str] = field(default_factory=list)        # Chỉ đạo chiến lược

@dataclass
class ActionItem:
    item_id: str                    # Mã công việc (ví dụ: ACT-01)
    task: str                       # Nội dung công việc cụ thể
    pic: str                        # Người phụ trách: định dạng Anh/Chị <Tên> (<Tag>)
    department: str                 # Bộ phận
    deadline: str                   # Hạn chót (VD: 15/11/2026 hoặc "Chưa xác định")
    evidence_quote: str = ""        # Trích dẫn câu nói trong transcript làm bằng chứng
    verified: bool = False          # Đã được kiểm chứng sự thật hay chưa

@dataclass
class FlaggedSegment:
    timestamp: str                  # [HH:MM:SS -> HH:MM:SS]
    speaker: str                    # Người nói
    raw_text: str                   # Đoạn âm thanh nghe không chắc chắn
    issue_type: str = "Đoạn [??]"   # Lý do gắn cờ

@dataclass
class MeetingAST:
    title: str = "BIÊN BẢN HỌP BÁO CÁO VẬN HÀNH & KẾ HOẠCH"
    date: str = "Chưa xác định"
    location: str = "Phòng họp Công ty TNHH Kiên Thành Tín"
    meeting_type: str = "bsc_kpi"   # kickoff | weekly | bsc_kpi
    chairperson: str = "Chị Thanh (BOD)"
    secretary: str = "Chưa xác định"
    attendees: List[Attendee] = field(default_factory=list)
    kpi_reports: List[KPIRecord] = field(default_factory=list)
    bod_evaluations: List[BODEvaluation] = field(default_factory=list)
    action_items: List[ActionItem] = field(default_factory=list)
    flagged_segments: List[FlaggedSegment] = field(default_factory=list)
    unresolved_questions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeetingAST":
        attendees = [Attendee(**a) for a in data.get("attendees", [])]
        kpi_reports = [KPIRecord(**k) for k in data.get("kpi_reports", [])]
        bod_evaluations = [BODEvaluation(**b) for b in data.get("bod_evaluations", [])]
        action_items = [ActionItem(**act) for act in data.get("action_items", [])]
        flagged_segments = [FlaggedSegment(**f) for f in data.get("flagged_segments", [])]

        return cls(
            title=data.get("title", ""),
            date=data.get("date", ""),
            location=data.get("location", ""),
            meeting_type=data.get("meeting_type", "bsc_kpi"),
            chairperson=data.get("chairperson", ""),
            secretary=data.get("secretary", ""),
            attendees=attendees,
            kpi_reports=kpi_reports,
            bod_evaluations=bod_evaluations,
            action_items=action_items,
            flagged_segments=flagged_segments,
            unresolved_questions=data.get("unresolved_questions", [])
        )

@dataclass
class Violation:
    gate_name: str                  # Tên chốt kiểm tra (ZeroHallucination, IdentityLinter...)
    severity: str                   # "CRITICAL" (buộc sửa) | "WARNING" (cảnh báo)
    location: str                   # Vị trí phát hiện (ví dụ: ActionItem #2)
    message: str                    # Mô tả chi tiết lỗi
    expected: str = ""              # Giá trị kỳ vọng
    actual: str = ""                # Giá trị thực tế sai lệch
    suggested_fix: str = ""         # Đề xuất sửa chữa cụ thể

@dataclass
class VerificationReport:
    passed: bool                    # True nếu không có lỗi CRITICAL
    total_violations: int = 0
    gate_results: Dict[str, bool] = field(default_factory=dict)
    violations: List[Violation] = field(default_factory=list)
    patch_instructions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
