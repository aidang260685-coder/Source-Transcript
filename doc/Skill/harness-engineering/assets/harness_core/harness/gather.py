"""Pha 1 - GATHER: gom dữ liệu thô từ nhiều nguồn, song song, chịu lỗi từng nguồn.

Nguyên tắc: GATHER chỉ thu và gắn nguồn gốc. Không lọc, không tóm tắt ở đây.
"""
from __future__ import annotations

import glob
import json
import sqlite3
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from typing import Callable, Protocol

from .models import RawItem, Task


class Source(Protocol):
    name: str
    def fetch(self, task: Task) -> list[RawItem]: ...


class FileSource:
    def __init__(self, pattern: str, name: str = "files") -> None:
        self.pattern, self.name = pattern, name

    def fetch(self, task: Task) -> list[RawItem]:
        items = []
        for path in sorted(glob.glob(self.pattern, recursive=True)):
            with open(path, encoding="utf-8", errors="replace") as f:
                items.append(RawItem(self.name, f.read(), uri=path))
        return items


class SQLiteSource:
    """sql dùng tham số `:query`. Luôn dùng tham số hoá, không nối chuỗi."""

    def __init__(self, db_path: str, sql: str, text_col: str = "text", name: str = "sqlite") -> None:
        self.db_path, self.sql, self.text_col, self.name = db_path, sql, text_col, name

    def fetch(self, task: Task) -> list[RawItem]:
        con = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)  # chỉ đọc
        con.row_factory = sqlite3.Row
        try:
            rows = con.execute(self.sql, {"query": task.query}).fetchall()
        finally:
            con.close()
        return [RawItem(self.name, str(r[self.text_col]), uri=f"{self.db_path}#{i}",
                        meta={k: r[k] for k in r.keys() if k != self.text_col})
                for i, r in enumerate(rows)]


class HTTPSource:
    """GET một URL (JSON hoặc text). Bắt buộc allowlist domain để tránh SSRF."""

    def __init__(self, url_template: str, allowed_hosts: set[str], name: str = "http",
                 json_path: str = "", timeout: float = 10.0) -> None:
        self.url_template, self.allowed, self.name = url_template, allowed_hosts, name
        self.json_path, self.timeout = json_path, timeout

    def fetch(self, task: Task) -> list[RawItem]:
        url = self.url_template.format(query=urllib.parse.quote(task.query))
        host = urllib.parse.urlparse(url).hostname or ""
        if host not in self.allowed:
            raise PermissionError(f"host không nằm trong allowlist: {host}")
        req = urllib.request.Request(url, headers={"User-Agent": "harness/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            body = r.read().decode("utf-8", "replace")
        if not self.json_path:
            return [RawItem(self.name, body, uri=url)]
        data = json.loads(body)
        for key in self.json_path.split("."):
            data = data[key]
        data = data if isinstance(data, list) else [data]
        return [RawItem(self.name, x if isinstance(x, str) else json.dumps(x, ensure_ascii=False),
                        uri=url) for x in data]


class CallableSource:
    def __init__(self, fn: Callable[[Task], list[RawItem]], name: str = "callable") -> None:
        self.fn, self.name = fn, name

    def fetch(self, task: Task) -> list[RawItem]:
        return self.fn(task)


class Gatherer:
    def __init__(self, sources: list[Source], per_source_timeout: float = 15.0,
                 retries: int = 1, backoff: float = 0.5) -> None:
        self.sources, self.timeout, self.retries, self.backoff = sources, per_source_timeout, retries, backoff
        self.errors: list[dict] = []

    def _fetch_one(self, src: Source, task: Task) -> list[RawItem]:
        last: Exception | None = None
        for i in range(self.retries + 1):
            try:
                return src.fetch(task)
            except PermissionError:
                raise                                   # lỗi chính sách: không retry
            except Exception as e:                      # noqa: BLE001 - nguồn lỗi không được làm sập vòng lặp
                last = e
                time.sleep(self.backoff * (2 ** i))
        raise last  # type: ignore[misc]

    def gather(self, task: Task) -> list[RawItem]:
        self.errors = []
        out: list[RawItem] = []
        with ThreadPoolExecutor(max_workers=max(1, len(self.sources))) as pool:
            futs = {pool.submit(self._fetch_one, s, task): s for s in self.sources}
            for fut, src in futs.items():
                try:
                    out.extend(fut.result(timeout=self.timeout))
                except (FutTimeout, Exception) as e:    # noqa: BLE001
                    self.errors.append({"source": src.name, "error": f"{type(e).__name__}: {e}"})
        return out
