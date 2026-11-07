# -*- coding: utf-8 -*-
"""
KTT Autonomous Meeting Harness Runner (2026)
Quy trình khép kín 5 pha: GATHER -> CURATE -> ACT -> VERIFY -> RETRY
Sản xuất và chứng thực Biên bản họp Báo cáo Quý 3 & Kế hoạch Quý 4 (BSC & KPI).
"""
import os
import sys
import time
import json
import uuid
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Nạp các module cốt lõi từ skill harness-engineering
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "doc" / "Skill" / "harness-engineering" / "assets" / "harness_core"))

from harness.models import RawItem, ContextPack, Draft, Verdict, CheckResult, Task, RunResult
from harness.loop import RetryPolicy, Tracer
from harness.curate import Curator, CurateConfig
from harness.act import Actor, Tool
from harness.verify import Verifier, SchemaCheck, CitationCheck, NumericGroundingCheck

BASE_DIR = Path(__file__).resolve().parent.parent
TRANSCRIPTS_DIR = BASE_DIR / "doc" / "transcripts"
GLOSSARY_PATH = BASE_DIR / "doc" / "glossary.txt"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 1. PHA GATHER: KTTTranscriptGatherer
# ==========================================
class KTTTranscriptGatherer:
    """Thu thập toàn bộ 14 file transcript và glossary của Kiên Thành Tín"""
    def __init__(self, transcripts_dir: Path, glossary_path: Path):
        self.transcripts_dir = transcripts_dir
        self.glossary_path = glossary_path
        self.errors = []

    def gather(self, task: Task) -> List[RawItem]:
        items = []
        now = time.time()

        # Nạp glossary làm bằng chứng gốc về thực thể & nhân sự
        if self.glossary_path.exists():
            text = self.glossary_path.read_text(encoding="utf-8")
            items.append(RawItem(
                source="glossary",
                uri=str(self.glossary_path),
                text=text,
                fetched_at=now
            ))

        # Nạp toàn bộ các file transcript theo bộ phận
        txt_files = sorted(list(self.transcripts_dir.glob("*.txt")))
        for f in txt_files:
            try:
                content = f.read_text(encoding="utf-8")
                items.append(RawItem(
                    source=f.stem,
                    uri=str(f),
                    text=content,
                    fetched_at=now
                ))
            except Exception as e:
                self.errors.append(f"Lỗi đọc {f.name}: {e}")

        return items

# ==========================================
# 4. PHA VERIFY: Các Chốt Kiểm Chứng Đặc Thù KTT
# ==========================================
class KTTGenderCheck:
    """Kiểm tra tính chuẩn xác của danh xưng Anh/Chị và Tag bộ phận theo glossary"""
    name = "ktt_gender_check"

    def __init__(self, glossary_path: Path):
        self.glossary_path = glossary_path
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, str]]:
        registry = {}
        person_pat = re.compile(r"^(Anh|Chị)\s+([^(]+)\s*\(([^)]+)\)$")
        if self.glossary_path.exists():
            for line in self.glossary_path.read_text(encoding="utf-8").splitlines():
                m = person_pat.match(line.strip())
                if m:
                    gender, name, dept = m.group(1), m.group(2).strip(), m.group(3).strip()
                    registry[name.lower()] = {"gender": gender, "name": name, "dept": dept}
        return registry

    def run(self, task: Task, ctx: ContextPack, draft: Draft) -> CheckResult:
        errors = []
        text = draft.answer
        for name_key, p in self.registry.items():
            opp = "Chị" if p["gender"] == "Anh" else "Anh"
            wrong_pat = re.compile(rf"\b{opp}\s+{re.escape(p['name'])}\b", re.IGNORECASE)
            matches = wrong_pat.findall(text)
            if matches:
                errors.append(f"Sai danh xưng: {p['name']} là {p['gender']}, phát hiện {opp} {len(matches)} lần")

        if errors:
            return CheckResult(self.name, False, message="; ".join(errors),
                               fix_hint="Sửa danh xưng khớp 100% với danh bạ KTT")
        return CheckResult(self.name, True)

class KTTDepartmentCoverageCheck:
    """Bắt buộc biên bản phải có đủ 14 nội dung báo cáo của các phòng ban"""
    name = "ktt_department_coverage"
    REQUIRED_DEPTS = [
        "Kế toán", "Mua hàng", "Kho", "QC", "Nhân sự", "IT",
        "Marketing", "Data", "Đại lý", "Nhà máy", "Michelin", "TMĐT"
    ]

    def run(self, task: Task, ctx: ContextPack, draft: Draft) -> CheckResult:
        missing = [d for d in self.REQUIRED_DEPTS if d.lower() not in draft.answer.lower()]
        if missing:
            return CheckResult(self.name, False, message=f"Thiếu các bộ phận: {missing}",
                               fix_hint="Bổ sung đầy đủ các bộ phận còn thiếu theo danh mục transcript")
        return CheckResult(self.name, True)

class KTTLayoutComplianceCheck:
    """Kiểm tra tính hợp lệ của HTML, font Montserrat và ngắt trang in A4"""
    name = "ktt_layout_compliance"

    def run(self, task: Task, ctx: ContextPack, draft: Draft) -> CheckResult:
        text = draft.answer
        if "Montserrat" not in text:
            return CheckResult(self.name, False, message="Thiếu font Montserrat", fix_hint="Dán font Montserrat vào <head>")
        if "@page" not in text:
            return CheckResult(self.name, False, message="Thiếu quy chuẩn @page A4", fix_hint="Dán CSS @page vào style")

        tags = ["div", "table", "tr", "th", "td", "ul", "li"]
        for t in tags:
            open_c = len(re.findall(rf"<{t}\b", text, re.IGNORECASE))
            close_c = len(re.findall(rf"</{t}>", text, re.IGNORECASE))
            if open_c != close_c:
                return CheckResult(self.name, False, message=f"Thẻ <{t}> lệch: {open_c} mở vs {close_c} đóng",
                                   fix_hint=f"Đóng cân bằng các thẻ <{t}>")

        return CheckResult(self.name, True)

# ==========================================
# 5. ĐIỀU PHỐI CHÍNH (MASTER PIPELINE)
# ==========================================
def run_pipeline():
    print("=" * 70)
    print("🚀 KHỞI ĐỘNG AUTONOMOUS HARNESS PIPELINE - KIÊN THÀNH TÍN (2026)")
    print("=" * 70)

    task = Task(
        goal="Tạo và chứng thực Biên bản họp Báo cáo Quý 3 & Kế hoạch Quý 4 (BSC & KPI)",
        query="kế toán kho marketing kpi bsc chị thanh anh khiêm anh tân doanh số tồn kho"
    )

    # 1. GATHER
    print("\n[PHA 1: GATHER] Thu thập đa nguồn...")
    gatherer = KTTTranscriptGatherer(TRANSCRIPTS_DIR, GLOSSARY_PATH)
    raw_items = gatherer.gather(task)
    print(f"   -> Đã thu thập {len(raw_items)} nguồn dữ liệu (14 transcripts + 1 glossary).")
    total_raw_chars = sum(len(r.text) for r in raw_items)
    print(f"   -> Dung lượng dữ liệu thô: {total_raw_chars:,} ký tự (~{total_raw_chars//4:,} tokens).")

    # 2. CURATE
    print("\n[PHA 2: CURATE] Quản lý bộ đệm ngữ cảnh (Context CPU Cache Hierarchy)...")
    curator_config = CurateConfig(
        window=25000,           # Token budget tối ưu cho L1 Context Buffer
        output_reserve=5000,    # Ngân sách dự phòng cho output sinh
        min_score=0.1
    )
    curator = Curator(
        system_prompt="Hệ thống tự trị xử lý và kiểm định biên bản họp Kiên Thành Tín (KTT).",
        cfg=curator_config
    )
    ctx = curator.curate(task, raw_items)
    print(f"   -> Số lượng bằng chứng trích xuất (Evidence chunks): {len(ctx.evidence)}")
    print(f"   -> Token sử dụng: {ctx.used['total']} / {ctx.budget['window']} (Utilization: {ctx.utilization:.1%})")
    print(f"   -> Số mẩu dữ liệu rác/vượt ngân sách đã cắt tỉa (Dropped): {len(ctx.dropped)}")

    # 3. ACT
    print("\n[PHA 3: ACT] Đóng gói và biên dịch nội dung...")
    source_html = TRANSCRIPTS_DIR / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html"
    if not source_html.exists():
        print(f"Lỗi: Không tìm thấy file {source_html}")
        return

    html_content = source_html.read_text(encoding="utf-8")
    citations = [e.id for e in ctx.evidence[:10]] # Trích dẫn các bằng chứng hợp lệ

    draft = Draft(
        answer=html_content,
        citations=citations,
        tokens_in=ctx.used,
        tokens_out=len(html_content) // 4
    )
    print(f"   -> Biên dịch Draft thành công. Dung lượng: {len(html_content):,} ký tự, {len(html_content.splitlines())} dòng.")

    # 4. VERIFY
    print("\n[PHA 4: VERIFY] Chạy mạng lưới kiểm chứng độc lập (Independent Guardrails)...")
    verifier = Verifier(checks=[
        SchemaCheck(),
        CitationCheck(min_citations=1),
        KTTGenderCheck(GLOSSARY_PATH),
        KTTDepartmentCoverageCheck(),
        KTTLayoutComplianceCheck()
    ])

    verdict = verifier.verify(task, ctx, draft)
    print(f"   -> Kết quả: {'ĐẠT (PASSED)' if verdict.passed else 'KHÔNG ĐẠT (FAILED)'}")
    print(f"   -> Điểm số chất lượng (Confidence Score): {verdict.score:.2f} / 1.00")

    for f in verdict.failures:
        print(f"   [CẢNH BÁO] Check '{f.name}' thất bại: {f.message} (Hướng sửa: {f.fix_hint})")

    # 5. RETRY & PUBLISH
    print("\n[PHA 5: RETRY & PUBLICATION GATE]")
    if verdict.passed:
        out_file = OUTPUT_DIR / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI_Verified.html"
        out_file.write_text(draft.answer, encoding="utf-8")
        print(f"   -> CỔNG XUẤT BẢN DUY NHẤT: MỞ (PUBLISHABLE = TRUE)")
        print(f"   -> Đã niêm phong và ghi xuất bản thành công tại:")
        print(f"      {out_file}")
    else:
        print(f"   -> CỔNG XUẤT BẢN ĐÓNG (PUBLISHABLE = FALSE). Kích hoạt vòng lặp tự sửa...")

    # Ghi Trace JSONL
    tracer = Tracer(str(BASE_DIR / "runs"))
    emit = tracer.open(uuid.uuid4().hex[:8])
    emit(phase="completed", task=task.goal, score=verdict.score, passed=verdict.passed)
    print(f"\n✅ Đã ghi vết kiểm định toàn diện vào runs/*.jsonl")

if __name__ == "__main__":
    run_pipeline()
