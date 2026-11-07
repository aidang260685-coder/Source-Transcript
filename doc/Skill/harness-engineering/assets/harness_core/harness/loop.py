"""Vòng lặp Harness: GATHER -> CURATE -> ACT -> VERIFY -> RETRY, có chặn trần và ghi vết."""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass

from .act import Actor
from .curate import Curator
from .gather import Gatherer
from .models import Draft, RunResult, Task, Verdict
from .verify import Verifier


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    max_seconds: float = 120.0
    max_total_tokens: int = 200_000     # tổng token cả vòng đời; chặn chi phí chạy lạc
    backoff: float = 0.0                # giây, nhân đôi mỗi lần; để 0 trong test
    regather_once: bool = True          # cho phép thu thập lại tối đa 1 lần khi thiếu bằng chứng


class Tracer:
    """JSONL mỗi lần chạy. Không có vết thì không debug và không đo được chi phí."""

    def __init__(self, directory: str | None = "runs") -> None:
        self.dir = directory

    def open(self, run_id: str):
        if not self.dir:
            return lambda **_: None
        os.makedirs(self.dir, exist_ok=True)
        path = os.path.join(self.dir, f"{run_id}.jsonl")

        def emit(**ev):
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"t": round(time.time(), 3), **ev}, ensure_ascii=False, default=str) + "\n")
        return emit


class Harness:
    def __init__(self, gatherer: Gatherer, curator: Curator, actor: Actor, verifier: Verifier,
                 policy: RetryPolicy | None = None, tracer: Tracer | None = None) -> None:
        self.g, self.c, self.a, self.v = gatherer, curator, actor, verifier
        self.policy, self.tracer = policy or RetryPolicy(), tracer or Tracer()

    def run(self, task: Task) -> RunResult:
        p, run_id, t0 = self.policy, uuid.uuid4().hex[:8], time.time()
        emit = self.tracer.open(run_id)
        emit(phase="start", goal=task.goal)

        # 1. GATHER (một lần; chỉ thu lại khi VERIFY chỉ ra thiếu bằng chứng)
        raw = self.g.gather(task)
        emit(phase="gather", items=len(raw), errors=self.g.errors)

        best: tuple[Draft, Verdict] | None = None
        feedback, prev_sig, stagnant, widen, regathered, tokens = "", "", 0, 1.0, False, 0
        for attempt in range(1, p.max_attempts + 1):
            if time.time() - t0 > p.max_seconds or tokens > p.max_total_tokens:
                return self._finish("escalated", best, attempt - 1, run_id, "vượt trần thời gian/token", emit)

            # 2. CURATE
            ctx = self.c.curate(task, raw, widen=widen, feedback=feedback)
            emit(phase="curate", attempt=attempt, evidence=len(ctx.evidence), used=ctx.used,
                 utilization=round(ctx.utilization, 3), dropped=len(ctx.dropped))

            # 3. ACT
            draft = self.a.act(task, ctx)
            tokens += draft.tokens_in + draft.tokens_out
            emit(phase="act", attempt=attempt, tools=[(r.tool, r.ok) for r in draft.tool_records],
                 tokens_in=draft.tokens_in, tokens_out=draft.tokens_out)

            # 4. VERIFY
            verdict = self.v.verify(task, ctx, draft)
            emit(phase="verify", attempt=attempt, passed=verdict.passed, score=verdict.score,
                 failures=[(f.name, f.message) for f in verdict.failures])
            if best is None or verdict.score >= best[1].score:
                best = (draft, verdict)
            if verdict.passed:
                return self._finish("verified", (draft, verdict), attempt, run_id, "", emit)

            # 5. RETRY: sửa có chủ đích, không chạy lại mù quáng
            stagnant = stagnant + 1 if verdict.signature == prev_sig else 0
            prev_sig = verdict.signature
            if stagnant >= 1 and widen > 1.0:
                return self._finish("escalated", best, attempt, run_id,
                                    "lỗi lặp lại sau khi đổi chiến lược: cần con người xem", emit)
            if verdict.needs_evidence:
                widen = 2.0
                if p.regather_once and not regathered:
                    raw += self.g.gather(task); regathered = True
                    emit(phase="regather", items=len(raw))
            elif stagnant >= 1:
                widen = 2.0                     # đổi chiến lược: lấy rộng hơn
            feedback = verdict.feedback()
            if p.backoff:
                time.sleep(p.backoff * 2 ** (attempt - 1))
        return self._finish("rejected", best, p.max_attempts, run_id, "hết số lần thử", emit)

    @staticmethod
    def _finish(status, best, attempts, run_id, reason, emit) -> RunResult:
        draft, verdict = best if best else (None, None)
        emit(phase="end", status=status, attempts=attempts, reason=reason)
        return RunResult(status, draft, verdict, attempts, run_id, reason)
