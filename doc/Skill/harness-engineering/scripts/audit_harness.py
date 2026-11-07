#!/usr/bin/env python3
"""Kiểm tra một thư mục dự án xem đã có Harness 5 pha chưa. Chỉ đọc, không sửa gì.

Dùng:  python audit_harness.py [đường_dẫn] [--json]
Mã thoát: 0 = đủ 5 pha + các cổng an toàn, 1 = thiếu.
"""
import json
import os
import re
import sys

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", "runs"}
EXT = {".py", ".ts", ".js", ".go", ".java", ".rs", ".md", ".toml", ".yaml", ".yml"}

# (pha, các mẫu tín hiệu). Khớp mẫu nghĩa là "có dấu hiệu", chưa chắc đúng; xem phần đánh giá chất lượng trong SKILL.md.
SIGNALS = {
    "GATHER": [r"\bclass \w*(Source|Gatherer|Scraper|Collector)\b", r"def gather\b", r"requests\.get|httpx|urllib\.request|sqlite3|psycopg|aiohttp"],
    "CURATE": [r"\bclass \w*(Curator|Ranker|Compressor)\b", r"def curate\b", r"token(s)?_?(budget|limit|count)|count_tokens|estimate_tokens|context_window|window_size", r"dedup|bm25|rerank"],
    "ACT": [r"\bclass \w*(Orchestrator|ToolRegistry|Actor)\b", r"tool_use|function_call|tools=\[|allowlist", r"def act\b"],
    "VERIFY": [r"\bclass \w*(Verifier|Judge|Evaluator)\b", r"def verify\b", r"grounded|citation|llm_judge|fail.?closed"],
    "RETRY": [r"max_attempts|max_retries|RetryPolicy", r"stagnat|backoff", r"escalat"],
}
GUARDS = {
    "trace/ghi vết": r"\.jsonl|tracer|Tracer|opentelemetry|structlog",
    "trần chi phí": r"max_total_tokens|max_seconds|budget",
    "test": r"unittest|pytest|def test_",
    "cổng xuất bản": r"publishable|status\s*==\s*['\"]verified",
}


def scan(root):
    hits = {k: set() for k in SIGNALS}
    guards = {k: False for k in GUARDS}
    files = 0
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for n in names:
            if os.path.splitext(n)[1] not in EXT:
                continue
            try:
                text = open(os.path.join(d, n), encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            files += 1
            for phase, pats in SIGNALS.items():
                for p in pats:
                    if re.search(p, text):
                        hits[phase].add(os.path.relpath(os.path.join(d, n), root))
            for g, p in GUARDS.items():
                guards[g] = guards[g] or bool(re.search(p, text))
    return files, hits, guards


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = args[0] if args else "."
    files, hits, guards = scan(root)
    missing = [p for p, f in hits.items() if not f]
    weak = [g for g, ok in guards.items() if not ok]
    report = {"root": os.path.abspath(root), "files_scanned": files,
              "phases": {p: sorted(f)[:5] for p, f in hits.items()},
              "missing_phases": missing, "missing_guards": weak,
              "verdict": "COMPLETE" if not missing and not weak else ("PARTIAL" if len(missing) < 5 else "ABSENT")}
    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Thư mục: {report['root']}  ({files} file)")
        for p in SIGNALS:
            print(f"  [{'x' if hits[p] else ' '}] {p:7s} {', '.join(sorted(hits[p])[:3])}")
        for g, ok in guards.items():
            print(f"  [{'x' if ok else ' '}] {g}")
        print("Kết luận:", report["verdict"])
    sys.exit(0 if report["verdict"] == "COMPLETE" else 1)


if __name__ == "__main__":
    main()
