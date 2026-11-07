"""Pha 4 - VERIFY: kiểm chứng độc lập trước khi xuất bản.

"Độc lập" nghĩa là: verifier không thấy lý lẽ trung gian của actor, ưu tiên kiểm tra
tất định (code) trước, và nếu dùng LLM làm giám khảo thì dùng một client/prompt riêng.
Người tự chấm bài của chính mình thì thường cho điểm cao.
"""
from __future__ import annotations

import re
from typing import Protocol

from .act import extract_json
from .llm import LLMClient
from .models import CheckResult, ContextPack, Draft, Task, Verdict

_NUM = re.compile(r"\d[\d.,]*\d|\d")


class Check(Protocol):
    name: str
    def run(self, task: Task, ctx: ContextPack, draft: Draft) -> CheckResult: ...


class SchemaCheck:
    name = "schema"

    def run(self, task, ctx, draft):
        if not draft.answer.strip():
            return CheckResult(self.name, False, message="câu trả lời rỗng",
                               fix_hint="trả JSON có trường answer không rỗng")
        return CheckResult(self.name, True)


class CitationCheck:
    """Mọi trích dẫn phải trỏ tới bằng chứng có thật trong ngữ cảnh (chống bịa nguồn)."""
    name = "citations"

    def __init__(self, min_citations: int = 1) -> None:
        self.min = min_citations

    def run(self, task, ctx, draft):
        valid = {e.id for e in ctx.evidence}
        bad = [c for c in draft.citations if c not in valid]
        if bad:
            return CheckResult(self.name, False, message=f"trích dẫn không tồn tại: {bad}",
                               fix_hint=f"chỉ dùng id trong {sorted(valid)}")
        if len(draft.citations) < self.min:
            return CheckResult(self.name, False, message="thiếu trích dẫn",
                               fix_hint="gắn id bằng chứng cho mọi dữ kiện", needs_evidence=not valid)
        return CheckResult(self.name, True)


class NumericGroundingCheck:
    """Mọi con số trong câu trả lời phải xuất hiện trong bằng chứng được trích dẫn."""
    name = "numeric_grounding"

    def run(self, task, ctx, draft):
        by_id = {e.id: e.text for e in ctx.evidence}
        src = " ".join(by_id.get(c, "") for c in draft.citations)
        src_nums = {n.strip(".,") for n in _NUM.findall(src)}
        ungrounded = sorted({n.strip(".,") for n in _NUM.findall(draft.answer)} - src_nums)
        if ungrounded:
            return CheckResult(self.name, False, message=f"số liệu không có trong bằng chứng: {ungrounded}",
                               fix_hint="xoá hoặc chỉ dùng số có trong bằng chứng đã trích dẫn",
                               needs_evidence=True)
        return CheckResult(self.name, True)


class LengthCheck:
    name = "length"

    def __init__(self, max_chars: int = 2000) -> None:
        self.max = max_chars

    def run(self, task, ctx, draft):
        ok = len(draft.answer) <= self.max
        return CheckResult(self.name, ok, message="" if ok else f"dài {len(draft.answer)} > {self.max} ký tự",
                           fix_hint="rút gọn")


class ForbiddenPatternCheck:
    """Chặn rò rỉ bí mật/PII trước khi xuất bản."""
    name = "forbidden_patterns"
    DEFAULT = [r"sk-[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"]

    def __init__(self, patterns: list[str] | None = None) -> None:
        self.rx = [re.compile(p) for p in (patterns or self.DEFAULT)]

    def run(self, task, ctx, draft):
        hit = [r.pattern for r in self.rx if r.search(draft.answer)]
        return CheckResult(self.name, not hit, message=f"khớp mẫu cấm: {hit}" if hit else "",
                           fix_hint="loại bỏ thông tin nhạy cảm")


JUDGE_SYSTEM = """Bạn là giám khảo độc lập. Chỉ dựa vào NHIỆM VỤ, BẰNG CHỨNG và BẢN NHÁP.
Chấm theo tiêu chí. Trả duy nhất JSON: {"score": 0..1, "pass": true|false, "issues": ["..."]}.
Nghi ngờ thì chấm thấp: một bản nháp có dữ kiện không được bằng chứng hỗ trợ phải bị loại."""


class LLMJudgeCheck:
    name = "llm_judge"

    def __init__(self, judge: LLMClient, rubric: str, threshold: float = 0.75) -> None:
        self.judge, self.rubric, self.threshold = judge, rubric, threshold

    def run(self, task, ctx, draft):
        prompt = (f"NHIỆM VỤ:\n{task.goal}\n\nTIÊU CHÍ:\n{self.rubric}\n\n"
                  f"BẰNG CHỨNG:\n{ctx.render_evidence()}\n\nBẢN NHÁP:\n{draft.answer}")
        obj = extract_json(self.judge.complete(JUDGE_SYSTEM, [{"role": "user", "content": prompt}], 512)) or {}
        score = float(obj.get("score", 0.0))
        ok = bool(obj.get("pass", False)) and score >= self.threshold
        return CheckResult(self.name, ok, message="; ".join(map(str, obj.get("issues", []))) or ("" if ok else "giám khảo không đạt hoặc trả JSON hỏng"),
                           fix_hint="sửa theo các vấn đề giám khảo nêu")


class Verifier:
    def __init__(self, checks: list[Check]) -> None:
        self.checks = checks

    def verify(self, task: Task, ctx: ContextPack, draft: Draft) -> Verdict:
        results: list[CheckResult] = []
        for ck in self.checks:
            try:
                results.append(ck.run(task, ctx, draft))
            except Exception as e:  # noqa: BLE001 - check hỏng = fail đóng (fail closed), không bao giờ cho qua
                results.append(CheckResult(ck.name, False, message=f"check lỗi: {type(e).__name__}: {e}"))
        errs = [r for r in results if r.severity == "error"]
        score = sum(r.passed for r in errs) / max(1, len(errs))
        return Verdict(all(r.passed for r in errs), round(score, 3), results)
