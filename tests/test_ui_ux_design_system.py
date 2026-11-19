# -*- coding: utf-8 -*-
"""
Test Suite: UI/UX Design System, DevTools (F12) & API Contract Verification
Kiểm tra tính nhất quán giữa Figma Tokens, CSS, HTML Semantic, WCAG 2.1 AA và API Contract.
"""
import json
import pytest
from pathlib import Path
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILL_ASSETS = ROOT_DIR / "doc" / "Skill" / "ui-ux-design-system" / "assets"
MEETING_ASSETS = ROOT_DIR / "doc" / "Skill" / "meeting-note" / "assets"

sys_script = ROOT_DIR / "doc" / "Skill" / "ui-ux-design-system" / "scripts" / "ui_audit_scanner.py"
import importlib.util
spec = importlib.util.spec_from_file_location("ui_audit_scanner", str(sys_script))
ui_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui_audit)


def test_design_tokens_json_schema():
    """Kiểm tra cấu trúc file Figma Design Tokens JSON."""
    tokens_file = SKILL_ASSETS / "design_tokens.json"
    assert tokens_file.exists(), "Thiếu file design_tokens.json"
    
    data = json.loads(tokens_file.read_text(encoding="utf-8"))
    assert "typography" in data
    assert "color" in data
    assert "spacing" in data
    assert "borderRadius" in data
    assert "shadow" in data
    assert "breakpoints" in data

    # Kiểm tra font Montserrat
    assert "Montserrat" in data["typography"]["fontFamily"]["primary"]
    # Kiểm tra màu chủ đạo KTT
    assert data["color"]["brand"]["primary"].upper() == "#1A56DB"


def test_design_tokens_css_variables():
    """Kiểm tra file CSS variables ánh xạ từ tokens."""
    css_file = SKILL_ASSETS / "design_tokens.css"
    assert css_file.exists(), "Thiếu file design_tokens.css"
    content = css_file.read_text(encoding="utf-8")

    assert "--ktt-font-primary" in content
    assert "Montserrat" in content
    assert "--ktt-color-primary" in content
    assert "#1A56DB" in content or "#1a56db" in content
    # Kiểm tra hệ lưới 8pt
    assert "--ktt-space-2: 0.5rem" in content   # 8px
    assert "--ktt-space-4: 1rem" in content     # 16px
    # Kiểm tra chuẩn in A4
    assert "@media print" in content
    assert "size: A4" in content


def test_standard_page_html_semantic_and_wcag():
    """Kiểm tra template trang mẫu chuẩn theo Accessibility và DevTools F12."""
    html_file = SKILL_ASSETS / "template_standard_page.html"
    assert html_file.exists(), "Thiếu file template_standard_page.html"
    
    issues = ui_audit.audit_html_file(html_file)
    critical_or_high = [i for i in issues if i["severity"] in {"CRITICAL", "HIGH"}]
    assert len(critical_or_high) == 0, f"Trang mẫu chuẩn có lỗi nghiêm trọng: {critical_or_high}"

    soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")
    # Kiểm tra landmarks semantic HTML5
    assert soup.find("header") is not None
    assert soup.find("main") is not None
    assert soup.find("footer") is not None
    assert soup.find("nav") is not None


def test_api_contract_validation_success_and_error():
    """Kiểm tra hợp đồng giao tiếp Frontend ↔ Backend (Envelope & RFC 7807)."""
    # 1. Hợp đồng thành công hợp lệ
    valid_success = {
        "success": True,
        "data": {"id": "101", "name": "BOD Review"},
        "meta": {"page": 1, "limit": 20}
    }
    errs = ui_audit.validate_api_contract(valid_success, is_error=False)
    assert len(errs) == 0

    # 2. Hợp đồng thành công vi phạm (thiếu data)
    invalid_success = {"success": True}
    errs = ui_audit.validate_api_contract(invalid_success, is_error=False)
    assert len(errs) > 0

    # 3. Hợp đồng lỗi chuẩn RFC 7807
    valid_error = {
        "type": "https://api.ktt.vn/errors/forbidden",
        "title": "Truy cập bị từ chối",
        "status": 403,
        "detail": "Người dùng không có quyền truy cập biên bản này."
    }
    errs = ui_audit.validate_api_contract(valid_error, is_error=True)
    assert len(errs) == 0

    # 4. Hợp đồng lỗi thiếu trường
    invalid_error = {"status": 500}
    errs = ui_audit.validate_api_contract(invalid_error, is_error=True)
    assert len(errs) > 0
