"""Giao diện LLM tối thiểu. Harness không phụ thuộc nhà cung cấp nào."""
from __future__ import annotations

import os
from typing import Callable, Protocol


class LLMClient(Protocol):
    def complete(self, system: str, messages: list[dict], max_tokens: int = 1024) -> str: ...


class AnthropicClient:
    """Cần `pip install anthropic` và biến môi trường ANTHROPIC_API_KEY."""

    def __init__(self, model: str | None = None) -> None:
        import anthropic  # import muộn để lõi vẫn chạy được khi không cài SDK

        self._client = anthropic.Anthropic()
        self.model = model or os.environ.get("HARNESS_MODEL", "claude-sonnet-5-5")

    def complete(self, system: str, messages: list[dict], max_tokens: int = 1024) -> str:
        resp = self._client.messages.create(
            model=self.model, system=system, messages=messages, max_tokens=max_tokens
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


class ScriptedLLM:
    """LLM giả cho test/demo: truyền vào hàm (system, messages) -> str."""

    def __init__(self, responder: Callable[[str, list[dict]], str]) -> None:
        self.responder = responder
        self.calls = 0

    def complete(self, system: str, messages: list[dict], max_tokens: int = 1024) -> str:
        self.calls += 1
        return self.responder(system, messages)
