# -*- coding: utf-8 -*-
"""
Harness Engineering Framework (2026)
Hệ thống Nhận thức & Điều phối Tự trị Khép kín:
  GATHER -> CURATE -> ACT -> VERIFY -> RETRY

Phục vụ xử lý biên bản họp, chuẩn hoá danh xưng & bảo toàn sự thật (Zero Hallucination)
cho Công ty TNHH Kiên Thành Tín (KTT).
"""

__version__ = "2026.1.0"
__author__ = "Senior AI Cognitive System Architect"

from .orchestrator import AutonomousMeetingHarness
from .schemas import MeetingAST, VerificationReport, ActionItem, Attendee

__all__ = [
    "AutonomousMeetingHarness",
    "MeetingAST",
    "VerificationReport",
    "ActionItem",
    "Attendee",
]
