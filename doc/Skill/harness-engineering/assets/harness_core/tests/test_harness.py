import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from harness import *  # noqa: F401,F403
from harness.curate import clean
from harness.act import extract_json

DATA = os.path.join(os.path.dirname(__file__), "..", "examples", "data", "*.txt")
TASK = Task("Tóm tắt doanh thu quý 3", query="doanh thu quý 3")


def mk(llm, checks=None, policy=None, cfg=None, sources=None):
    return Harness(Gatherer(sources or [FileSource(DATA)], backoff=0), Curator("sys", cfg or CurateConfig(window=4000, output_reserve=500)),
                   Actor(llm), Verifier(checks or [SchemaCheck(), CitationCheck(), NumericGroundingCheck()]),
                   policy or RetryPolicy(), Tracer(tempfile.mkdtemp()))


class Gather(unittest.TestCase):
    def test_source_failure_is_isolated(self):
        def boom(task): raise RuntimeError("down")
        g = Gatherer([FileSource(DATA), CallableSource(boom, "bad")], retries=0, backoff=0)
        items = g.gather(TASK)
        self.assertTrue(items)
        self.assertEqual(g.errors[0]["source"], "bad")

    def test_http_allowlist(self):
        g = Gatherer([HTTPSource("http://evil.example/{query}", {"api.good.com"})], retries=0, backoff=0)
        g.gather(TASK)
        self.assertIn("allowlist", g.errors[0]["error"])


class Curate(unittest.TestCase):
    def raw(self):
        return Gatherer([FileSource(DATA)]).gather(TASK)

    def test_dedupe_and_noise(self):
        ctx = Curator("s", CurateConfig(window=4000, output_reserve=500)).curate(TASK, self.raw())
        self.assertEqual(sum("120 tỷ" in e.text for e in ctx.evidence), 1)   # bản trùng bị loại
        self.assertTrue(any(d["why"] == "near_duplicate" for d in ctx.dropped))
        self.assertNotIn("Subscribe", ctx.render_evidence())

    def test_relevance_ordering(self):
        ctx = Curator("s", CurateConfig(window=4000, output_reserve=500)).curate(TASK, self.raw())
        self.assertIn("120 tỷ", ctx.evidence[0].text)

    def test_budget_is_hard_cap(self):
        big = [RawItem("x", ("Doanh thu quý 3 tăng mạnh. " * 40 + f"Câu số {i}. ") * 5, uri=str(i)) for i in range(30)]
        cfg = CurateConfig(window=1200, output_reserve=300, max_per_source=100)
        ctx = Curator("s", cfg).curate(TASK, big)
        self.assertLessEqual(ctx.used["total"], cfg.window)
        self.assertTrue(ctx.evidence)

    def test_clean_strips_html(self):
        self.assertNotIn("<b>", clean("<b>hello world</b> đây là nội dung đủ dài để giữ lại"))


class Act(unittest.TestCase):
    def test_extract_json_tolerant(self):
        self.assertEqual(extract_json('chữ thừa ```json\n{"a": {"b": "}"}}\n``` xong'), {"a": {"b": "}"}})

    def test_tool_roundtrip_and_errors(self):
        reg = ToolRegistry([Tool("add", "cộng", lambda a, b: a + b, required=("a", "b"))])
        self.assertEqual(reg.call("add", {"a": 1, "b": 2}).output, "3")
        self.assertFalse(reg.call("add", {"a": 1}).ok)         # thiếu tham số
        self.assertFalse(reg.call("rm_rf", {}).ok)             # không nằm trong allowlist

    def test_actor_uses_tool_then_answers(self):
        seq = iter(['{"tool":"add","args":{"a":2,"b":3}}', '{"answer":"5","citations":[]}'])
        reg = ToolRegistry([Tool("add", "cộng", lambda a, b: a + b, required=("a", "b"))])
        d = Actor(ScriptedLLM(lambda s, m: next(seq)), reg).act(TASK, Curator("s").curate(TASK, []))
        self.assertEqual(d.answer, "5")
        self.assertEqual(d.tool_records[0].output, "5")


class Verify(unittest.TestCase):
    def ctx(self):
        return Curator("s").curate(TASK, Gatherer([FileSource(DATA)]).gather(TASK))

    def test_catches_fabricated_number_and_citation(self):
        ctx = self.ctx()
        v = Verifier([CitationCheck(), NumericGroundingCheck()])
        self.assertFalse(v.verify(TASK, ctx, Draft("tăng 18%", ["e1"])).passed)
        self.assertFalse(v.verify(TASK, ctx, Draft("tăng 15%", ["e99"])).passed)
        self.assertTrue(v.verify(TASK, ctx, Draft("tăng 15%", ["e1"])).passed)

    def test_secret_blocked(self):
        v = Verifier([ForbiddenPatternCheck()])
        self.assertFalse(v.verify(TASK, self.ctx(), Draft("key sk-" + "a" * 30, [])).passed)

    def test_broken_check_fails_closed(self):
        class Bad:
            name = "bad"
            def run(self, *a): raise RuntimeError("x")
        self.assertFalse(Verifier([Bad()]).verify(TASK, self.ctx(), Draft("x", ["e1"])).passed)

    def test_llm_judge(self):
        j = LLMJudgeCheck(ScriptedLLM(lambda s, m: '{"score": 0.9, "pass": true, "issues": []}'), "chính xác")
        self.assertTrue(Verifier([j]).verify(TASK, self.ctx(), Draft("ok", ["e1"])).passed)


class Loop(unittest.TestCase):
    def test_retry_fixes_hallucination(self):
        def llm(s, m):
            retried = any("Phản hồi từ lần kiểm chứng" in x["content"] for x in m)
            return '{"answer":"tăng 15%","citations":["e1"]}' if retried else '{"answer":"tăng 18%","citations":["e1"]}'
        r = mk(ScriptedLLM(llm)).run(TASK)
        self.assertEqual((r.status, r.attempts, r.publishable), ("verified", 2, True))

    def test_never_publishes_unverified(self):
        r = mk(ScriptedLLM(lambda s, m: '{"answer":"tăng 99%","citations":["e1"]}')).run(TASK)
        self.assertFalse(r.publishable)
        self.assertIn(r.status, ("rejected", "escalated"))

    def test_stagnation_escalates_early(self):
        llm = ScriptedLLM(lambda s, m: '{"answer":"tăng 99%","citations":["e1"]}')
        r = mk(llm, policy=RetryPolicy(max_attempts=6)).run(TASK)
        self.assertEqual(r.status, "escalated")
        self.assertLess(r.attempts, 6)                         # dừng sớm, không đốt token vô ích

    def test_token_ceiling(self):
        llm = ScriptedLLM(lambda s, m: '{"answer":"tăng 99%","citations":["e1"]}')
        r = mk(llm, policy=RetryPolicy(max_attempts=5, max_total_tokens=1)).run(TASK)
        self.assertEqual(r.status, "escalated")

    def test_trace_written(self):
        h = mk(ScriptedLLM(lambda s, m: '{"answer":"tăng 15%","citations":["e1"]}'))
        r = h.run(TASK)
        self.assertTrue(os.path.exists(os.path.join(h.tracer.dir, f"{r.run_id}.jsonl")))


if __name__ == "__main__":
    unittest.main()
