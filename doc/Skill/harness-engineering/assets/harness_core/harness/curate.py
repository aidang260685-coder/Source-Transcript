"""Pha 2 - CURATE: cửa sổ ngữ cảnh là bộ đệm CPU mới.

Mọi token đưa vào đều phải "trả tiền" bằng latency, chi phí và độ chính xác.
Curator làm 4 việc theo thứ tự: làm sạch -> khử trùng lặp -> chấm điểm -> đóng gói theo ngân sách.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Callable

from .models import ContextPack, Evidence, RawItem, Task

_WORD = re.compile(r"\w+", re.UNICODE)
_TAG = re.compile(r"<[^>]+>")
_SENT = re.compile(r"(?<=[.!?。])\s+|\n+")
BOILERPLATE = re.compile(
    r"(cookie|đăng ký nhận tin|subscribe|all rights reserved|bản quyền thuộc|"
    r"click here|đọc thêm|quảng cáo|advertisement)", re.I)


def estimate_tokens(text: str) -> int:
    """Ước lượng thô, an toàn. Tiếng Việt/CJK tốn token hơn tiếng Anh nên dùng hệ số bảo thủ.
    Thay bằng tokenizer thật của nhà cung cấp khi cần số liệu chính xác."""
    if not text:
        return 0
    non_ascii = sum(1 for c in text if ord(c) > 127) / len(text)
    return math.ceil(len(text) / (2.5 if non_ascii > 0.15 else 4))


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s).lower()


def _words(s: str) -> list[str]:
    return _WORD.findall(_norm(s))


def clean(text: str) -> str:
    text = _TAG.sub(" ", text)
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln and not BOILERPLATE.search(ln)]
    return re.sub(r"[ \t]+", " ", "\n".join(lines)).strip()


def _symbol_ratio(s: str) -> float:
    return sum(1 for c in s if not (c.isalnum() or c.isspace())) / max(1, len(s))


def _shingles(words: list[str], k: int = 3) -> set[tuple[str, ...]]:
    return {tuple(words[i:i + k]) for i in range(max(1, len(words) - k + 1))}


@dataclass
class CurateConfig:
    window: int = 16000            # tổng cửa sổ ngữ cảnh mục tiêu (token)
    output_reserve: int = 2000     # chừa chỗ cho câu trả lời + tool output
    safety_margin: float = 0.10    # sai số ước lượng token
    min_chars: int = 40
    max_symbol_ratio: float = 0.35
    dup_threshold: float = 0.80    # Jaccard shingle
    min_score: float = 0.0         # bỏ mẩu có điểm <= ngưỡng
    max_per_source: int = 8        # chống một nguồn "ăn" hết ngân sách


class Curator:
    def __init__(self, system_prompt: str, cfg: CurateConfig | None = None,
                 counter: Callable[[str], int] = estimate_tokens,
                 source_weight: dict[str, float] | None = None) -> None:
        self.system, self.cfg, self.count = system_prompt, cfg or CurateConfig(), counter
        self.source_weight = source_weight or {}

    # ---- bước 1+2: làm sạch và khử trùng lặp -------------------------------------------------
    def _filter(self, items: list[RawItem], dropped: list[dict]) -> list[RawItem]:
        kept: list[RawItem] = []
        sigs: list[set] = []
        for it in items:
            text = clean(it.text)
            if len(text) < self.cfg.min_chars:
                dropped.append({"id": it.id, "why": "too_short"}); continue
            if _symbol_ratio(text) > self.cfg.max_symbol_ratio:
                dropped.append({"id": it.id, "why": "symbol_noise"}); continue
            sh = _shingles(_words(text))
            if any(len(sh & o) / max(1, len(sh | o)) >= self.cfg.dup_threshold for o in sigs):
                dropped.append({"id": it.id, "why": "near_duplicate"}); continue
            sigs.append(sh)
            kept.append(RawItem(it.source, text, it.uri, it.meta, it.fetched_at))
        return kept

    # ---- bước 3: chấm điểm (BM25 rút gọn + trọng số nguồn) ----------------------------------
    def _score(self, items: list[RawItem], query: str) -> list[tuple[float, RawItem]]:
        q = set(_words(query))
        docs = [_words(i.text) for i in items]
        n, avgdl = len(docs), (sum(map(len, docs)) / max(1, len(docs)))
        df = Counter(w for d in docs for w in set(d) if w in q)
        out = []
        for it, d in zip(items, docs):
            tf, s = Counter(d), 0.0
            for w in q:
                if tf[w]:
                    idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
                    s += idf * tf[w] * 2.2 / (tf[w] + 1.2 * (0.25 + 0.75 * len(d) / max(1, avgdl)))
            out.append((s * self.source_weight.get(it.source, 1.0), it))
        return sorted(out, key=lambda x: -x[0])

    # ---- nén trích xuất: giữ câu liên quan nhất, KHÔNG viết lại (tránh sinh sai lệch) -----------
    def _compress(self, text: str, query: str, max_tokens: int) -> str:
        q = set(_words(query))
        sents = [s.strip() for s in _SENT.split(text) if s.strip()]
        ranked = sorted(range(len(sents)), key=lambda i: -len(q & set(_words(sents[i]))))
        chosen: list[int] = []
        used = 0
        for i in ranked:
            t = self.count(sents[i])
            if used + t > max_tokens:
                continue
            chosen.append(i); used += t
        return " ".join(sents[i] for i in sorted(chosen))

    # ---- bước 4: đóng gói theo ngân sách -------------------------------------------------------
    def curate(self, task: Task, raw: list[RawItem], widen: float = 1.0,
               feedback: str = "") -> ContextPack:
        """widen > 1 (dùng khi retry vì thiếu dữ kiện) nới hạn mức theo nguồn và bỏ ngưỡng điểm,
        để lấy rộng hơn. Ngân sách token tổng thì KHÔNG bao giờ được nới: window là trần cứng."""
        c = self.cfg
        dropped: list[dict] = []
        task_text = task.goal + (f"\n\nPhản hồi từ lần kiểm chứng trước:\n{feedback}" if feedback else "")
        fixed = self.count(self.system) + self.count(task_text)
        usable = int((c.window - c.output_reserve) * (1 - c.safety_margin))
        budget_ev = max(0, usable - fixed)
        quota = int(c.max_per_source * widen)
        floor = c.min_score if widen <= 1 else -1.0

        scored = [(s, it) for s, it in self._score(self._filter(raw, dropped), task.query)
                  if s > floor]
        per_src: Counter = Counter()
        evidence: list[Evidence] = []
        used_ev = 0
        for s, it in scored:
            if per_src[it.source] >= quota:
                dropped.append({"id": it.id, "why": "source_quota"}); continue
            text, comp = it.text, False
            t = self.count(text)
            room = budget_ev - used_ev
            if t > room:
                text, comp = self._compress(text, task.query, max(0, min(room, budget_ev // 3))), True
                t = self.count(text)
            if not text or t > room:
                dropped.append({"id": it.id, "why": "over_budget"}); continue
            evidence.append(Evidence(f"e{len(evidence) + 1}", text, it.source, it.uri, round(s, 3), t, comp))
            per_src[it.source] += 1
            used_ev += t
        used = {"system": self.count(self.system), "task": self.count(task_text),
                "evidence": used_ev, "output_reserve": c.output_reserve}
        used["total"] = used["system"] + used["task"] + used_ev + c.output_reserve
        return ContextPack(self.system, task_text, evidence,
                           {"window": c.window, "evidence": budget_ev}, used, dropped)
