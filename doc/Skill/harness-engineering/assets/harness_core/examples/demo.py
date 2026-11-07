"""Demo offline: LLM giả cố tình bịa số ở lượt 1, VERIFY bắt được, RETRY sửa ở lượt 2."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from harness import (Actor, CitationCheck, CurateConfig, Curator, FileSource, Gatherer, Harness,
                     NumericGroundingCheck, RetryPolicy, SchemaCheck, ScriptedLLM, Task, Tracer, Verifier)

DATA = os.path.join(os.path.dirname(__file__), "data", "*.txt")


def fake_llm(system, messages):
    retried = any("Phản hồi từ lần kiểm chứng" in m["content"] for m in messages if m["role"] == "user")
    if not retried:   # lượt 1: bịa con số 18%
        return '{"answer": "Doanh thu quý 3 đạt 120 tỷ đồng, tăng 18%.", "citations": ["e1"]}'
    return '{"answer": "Doanh thu quý 3 đạt 120 tỷ đồng, tăng 15% so với cùng kỳ.", "citations": ["e1"]}'


def build() -> Harness:
    return Harness(
        Gatherer([FileSource(DATA)]),
        Curator("Bạn là trợ lý phân tích số liệu, trả lời ngắn gọn.", CurateConfig(window=4000, output_reserve=500)),
        Actor(ScriptedLLM(fake_llm)),
        Verifier([SchemaCheck(), CitationCheck(), NumericGroundingCheck()]),
        RetryPolicy(max_attempts=3),
        Tracer("runs"),
    )


if __name__ == "__main__":
    res = build().run(Task("Tóm tắt doanh thu quý 3", query="doanh thu quý 3"))
    print("status     :", res.status, "| lần thử:", res.attempts, "| publishable:", res.publishable)
    print("answer     :", res.draft.answer if res.draft else None)
    print("trace      :", f"runs/{res.run_id}.jsonl")
