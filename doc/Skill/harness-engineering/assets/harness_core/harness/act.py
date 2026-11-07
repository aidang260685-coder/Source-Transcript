"""Pha 3 - ACT: bộ điều phối gọi công cụ.

Model chỉ *đề xuất* lời gọi công cụ bằng JSON. Orchestrator mới là bên thực thi, nên nó
kiểm soát allowlist, kiểm tra tham số, timeout và ghi nhật ký. Model không bao giờ chạm trực tiếp
vào hệ thống bên ngoài.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from dataclasses import dataclass, field
from typing import Any, Callable

from .curate import estimate_tokens
from .llm import LLMClient
from .models import ContextPack, Draft, Task, ToolRecord


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]
    required: tuple[str, ...] = ()
    timeout: float = 20.0
    side_effects: bool = False     # True => cần cơ chế idempotency/duyệt trước khi bật ở production


class ToolRegistry:
    def __init__(self, tools: list[Tool] | None = None) -> None:
        self._tools = {t.name: t for t in (tools or [])}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def describe(self) -> str:
        return "\n".join(f"- {t.name}({', '.join(t.required)}): {t.description}" for t in self._tools.values()) or "(không có)"

    def call(self, name: str, args: dict[str, Any]) -> ToolRecord:
        t0 = time.time()
        tool = self._tools.get(name)
        if tool is None:
            return ToolRecord(name, args, False, f"Công cụ không tồn tại: {name}", 0)
        missing = [k for k in tool.required if k not in args]
        if missing:
            return ToolRecord(name, args, False, f"Thiếu tham số: {missing}", 0)
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                out = pool.submit(tool.fn, **args).result(timeout=tool.timeout)
            return ToolRecord(name, args, True, str(out)[:4000], int((time.time() - t0) * 1000))
        except FutTimeout:
            return ToolRecord(name, args, False, "timeout", int((time.time() - t0) * 1000))
        except Exception as e:  # noqa: BLE001 - trả lỗi cho model như một quan sát, không làm sập vòng lặp
            return ToolRecord(name, args, False, f"{type(e).__name__}: {e}", int((time.time() - t0) * 1000))


def extract_json(text: str) -> dict | None:
    """Lấy đối tượng JSON đầu tiên cân bằng ngoặc, chịu được rào ```json và chữ thừa."""
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                esc = (ch == "\\") and not esc
                if ch == '"' and not esc:
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


ACT_PROTOCOL = """Bạn làm việc theo giao thức JSON, mỗi lượt chỉ trả MỘT đối tượng JSON:
- Gọi công cụ:  {"tool": "<tên>", "args": {...}}
- Kết thúc:     {"answer": "<câu trả lời>", "citations": ["e1", "e2"]}
Quy tắc: chỉ dùng dữ kiện trong BẰNG CHỨNG hoặc kết quả công cụ; mọi dữ kiện phải trích dẫn id bằng chứng;
nếu bằng chứng không đủ, nói rõ là không đủ thay vì đoán."""


class Actor:
    def __init__(self, llm: LLMClient, tools: ToolRegistry | None = None,
                 max_steps: int = 4, max_tokens: int = 1024) -> None:
        self.llm, self.tools, self.max_steps, self.max_tokens = llm, tools or ToolRegistry(), max_steps, max_tokens

    def act(self, task: Task, ctx: ContextPack) -> Draft:
        system = f"{ctx.system}\n\n{ACT_PROTOCOL}\n\nCÔNG CỤ:\n{self.tools.describe()}"
        user = f"NHIỆM VỤ:\n{ctx.task}\n\nBẰNG CHỨNG:\n{ctx.render_evidence() or '(trống)'}"
        messages: list[dict] = [{"role": "user", "content": user}]
        records: list[ToolRecord] = []
        t_in = t_out = 0
        for _ in range(self.max_steps):
            t_in += estimate_tokens(system) + sum(estimate_tokens(m["content"]) for m in messages)
            reply = self.llm.complete(system, messages, self.max_tokens)
            t_out += estimate_tokens(reply)
            obj = extract_json(reply)
            if obj is None:
                messages += [{"role": "assistant", "content": reply},
                             {"role": "user", "content": "Phản hồi không phải JSON hợp lệ. Hãy trả đúng một đối tượng JSON."}]
                continue
            if "tool" in obj:
                rec = self.tools.call(str(obj["tool"]), obj.get("args") or {})
                records.append(rec)
                messages += [{"role": "assistant", "content": reply},
                             {"role": "user", "content": f"KẾT QUẢ CÔNG CỤ {rec.tool} (ok={rec.ok}): {rec.output}"}]
                continue
            if "answer" in obj:
                return Draft(str(obj["answer"]), [str(c) for c in obj.get("citations", [])],
                             {k: v for k, v in obj.items() if k not in ("answer", "citations")},
                             records, t_in, t_out)
        return Draft("", [], {"error": "actor_exhausted_steps"}, records, t_in, t_out)
