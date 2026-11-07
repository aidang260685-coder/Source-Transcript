"""Kiểu dữ liệu dùng chung cho 5 pha của Harness. Chỉ dùng stdlib."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "ignore")).hexdigest()[:12]


@dataclass
class Task:
    goal: str                              # việc cần làm, ngôn ngữ tự nhiên
    query: str = ""                        # từ khoá truy hồi; mặc định = goal
    constraints: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.query = self.query or self.goal


@dataclass
class RawItem:
    """Dữ liệu thô từ GATHER. Luôn mang theo nguồn gốc (provenance)."""
    source: str
    text: str
    uri: str = ""
    meta: dict[str, Any] = field(default_factory=dict)
    fetched_at: float = field(default_factory=time.time)

    @property
    def id(self) -> str:
        return short_hash(f"{self.source}|{self.uri}|{self.text[:200]}")


@dataclass
class Evidence:
    """Một mẩu bằng chứng đã qua CURATE, có id ngắn để model trích dẫn."""
    id: str            # e1, e2, ...
    text: str
    source: str
    uri: str
    score: float
    tokens: int
    compressed: bool = False


@dataclass
class ContextPack:
    """Nội dung sẽ đưa vào cửa sổ ngữ cảnh + sổ cái token."""
    system: str
    task: str
    evidence: list[Evidence]
    budget: dict[str, int]
    used: dict[str, int]
    dropped: list[dict[str, Any]] = field(default_factory=list)

    @property
    def utilization(self) -> float:
        return self.used["total"] / max(1, self.budget["window"])

    def render_evidence(self) -> str:
        return "\n\n".join(f"[{e.id}] ({e.source}) {e.text}" for e in self.evidence)


@dataclass
class ToolRecord:
    tool: str
    args: dict[str, Any]
    ok: bool
    output: str
    ms: int


@dataclass
class Draft:
    """Kết quả của ACT: chưa được phép xuất bản cho tới khi VERIFY đạt."""
    answer: str
    citations: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    tool_records: list[ToolRecord] = field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0


@dataclass
class CheckResult:
    name: str
    passed: bool
    severity: str = "error"        # error | warn
    message: str = ""
    fix_hint: str = ""
    needs_evidence: bool = False   # True => retry nên GATHER thêm, không chỉ viết lại


@dataclass
class Verdict:
    passed: bool
    score: float
    results: list[CheckResult]

    @property
    def failures(self) -> list[CheckResult]:
        return [r for r in self.results if not r.passed and r.severity == "error"]

    @property
    def signature(self) -> str:
        """Dấu vân tay của lỗi: giống nhau 2 lần liên tiếp => đang dậm chân tại chỗ."""
        return short_hash("|".join(sorted(f"{r.name}:{r.message}" for r in self.failures)))

    @property
    def needs_evidence(self) -> bool:
        return any(r.needs_evidence for r in self.failures)

    def feedback(self) -> str:
        lines = [f"- {r.name}: {r.message}" + (f" => {r.fix_hint}" if r.fix_hint else "")
                 for r in self.failures]
        return "\n".join(lines)


@dataclass
class RunResult:
    status: str                    # verified | rejected | escalated
    draft: Draft | None
    verdict: Verdict | None
    attempts: int
    run_id: str
    reason: str = ""

    @property
    def publishable(self) -> bool:
        """Cổng xuất bản duy nhất: chỉ kết quả đã VERIFY mới được đi tiếp."""
        return self.status == "verified"
