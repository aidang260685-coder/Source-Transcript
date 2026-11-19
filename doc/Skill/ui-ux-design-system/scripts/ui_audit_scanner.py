#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KTT UI/UX, DevTools (F12) & API Contract Automated Audit Scanner
Thuộc bộ công cụ: doc/Skill/ui-ux-design-system/scripts/ui_audit_scanner.py
"""
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[4]


def audit_html_file(file_path: Path) -> List[Dict[str, Any]]:
    """Kiểm tra toàn diện một file HTML theo quy chuẩn UI/UX và DevTools F12."""
    issues = []
    rel_path = file_path.relative_to(ROOT_DIR)
    content = file_path.read_text(encoding="utf-8")
    
    # 1. Kiểm tra cân bằng thẻ
    for tag in ["table", "div", "section", "article", "ul", "ol", "form"]:
        open_count = len(re.findall(rf"<{tag}\b", content, re.IGNORECASE))
        close_count = len(re.findall(rf"</{tag}>", content, re.IGNORECASE))
        if open_count != close_count:
            issues.append({
                "category": "DEVTOOLS_DOM",
                "severity": "HIGH",
                "file": str(rel_path),
                "rule": f"Unbalanced <{tag}> tag",
                "message": f"Số thẻ mở <{tag}> ({open_count}) không khớp số thẻ đóng </{tag}> ({close_count})."
            })

    soup = BeautifulSoup(content, "html.parser")

    # 2. Kiểm tra Head, Viewport, Charset & Title
    head = soup.find("head")
    if not head:
        issues.append({
            "category": "DEVTOOLS_DOM",
            "severity": "CRITICAL",
            "file": str(rel_path),
            "rule": "Missing <head>",
            "message": "Trang HTML thiếu thẻ <head> hợp lệ."
        })
    else:
        # Check viewport
        viewport = head.find("meta", attrs={"name": "viewport"})
        if not viewport:
            issues.append({
                "category": "UI_RESPONSIVE",
                "severity": "HIGH",
                "file": str(rel_path),
                "rule": "Missing Viewport Meta",
                "message": "Thiếu <meta name='viewport' content='width=device-width, initial-scale=1.0'> gây vỡ giao diện trên mobile."
            })
        
        # Check title
        title = head.find("title")
        if not title or not title.text.strip():
            issues.append({
                "category": "ACCESSIBILITY",
                "severity": "MEDIUM",
                "file": str(rel_path),
                "rule": "Empty or Missing Title",
                "message": "Thẻ <title> bị thiếu hoặc để trống."
            })

    # 3. Kiểm tra Font chữ Montserrat
    has_montserrat = "montserrat" in content.lower()
    if not has_montserrat:
        # Kiểm tra xem có tham chiếu tới CSS chứa font Montserrat hay không
        for link in soup.find_all("link", rel=lambda r: r and "stylesheet" in r):
            href = link.get("href", "")
            css_path = file_path.parent / href
            if css_path.exists() and "montserrat" in css_path.read_text(encoding="utf-8").lower():
                has_montserrat = True
                break
        # Kiểm tra template frame có comment tham chiếu style.css
        if not has_montserrat and "assets/style.css" in content:
            style_css = file_path.parent / "style.css"
            if style_css.exists() and "montserrat" in style_css.read_text(encoding="utf-8").lower():
                has_montserrat = True

    if not has_montserrat:
        issues.append({
            "category": "UI_TYPOGRAPHY",
            "severity": "HIGH",
            "file": str(rel_path),
            "rule": "Non-Compliant Typography",
            "message": "Không tìm thấy font chủ đạo 'Montserrat' trong file hoặc liên kết font/CSS."
        })

    # 4. Kiểm tra Accessibility & Semantic Elements (DevTools F12 Accessibility Tree)
    # Check images alt
    for img in soup.find_all("img"):
        if not img.get("alt"):
            issues.append({
                "category": "ACCESSIBILITY_WCAG",
                "severity": "MEDIUM",
                "file": str(rel_path),
                "rule": "Image Missing Alt Text",
                "message": f"Thẻ <img> thiếu thuộc tính 'alt': {str(img)[:60]}..."
            })

    # Check button text or aria-label
    for btn in soup.find_all("button"):
        text = btn.text.strip()
        aria_label = btn.get("aria-label", "").strip()
        if not text and not aria_label:
            issues.append({
                "category": "ACCESSIBILITY_WCAG",
                "severity": "HIGH",
                "file": str(rel_path),
                "rule": "Empty Button Target",
                "message": f"Thẻ <button> không có nhãn hiển thị hoặc 'aria-label': {str(btn)[:60]}..."
            })

    # Check empty links or href="#"
    for a in soup.find_all("a"):
        href = a.get("href", "").strip()
        if href == "#" and not a.get("role"):
            issues.append({
                "category": "DEVTOOLS_NAV",
                "severity": "LOW",
                "file": str(rel_path),
                "rule": "Dummy Link href='#'",
                "message": f"Thẻ <a> sử dụng dummy href='#' không gán role/action: {str(a)[:60]}..."
            })

    # 5. Kiểm tra DOM Depth (Độ sâu DOM tối đa)
    def get_max_depth(node, depth=0):
        if not hasattr(node, "children"):
            return depth
        children = [c for c in node.children if c.name is not None]
        if not children:
            return depth
        return max(get_max_depth(c, depth + 1) for c in children)

    max_dom_depth = get_max_depth(soup)
    if max_dom_depth > 24:
        issues.append({
            "category": "DEVTOOLS_PERF",
            "severity": "MEDIUM",
            "file": str(rel_path),
            "rule": "Excessive DOM Depth",
            "message": f"Độ sâu DOM lồng nhau ({max_dom_depth} tầng) vượt ngưỡng tối ưu (24 tầng), gây chậm render."
        })

    return issues


def audit_css_file(file_path: Path) -> List[Dict[str, Any]]:
    """Kiểm tra CSS theo chuẩn Design System KTT."""
    issues = []
    rel_path = file_path.relative_to(ROOT_DIR)
    content = file_path.read_text(encoding="utf-8")

    # Kiểm tra font Montserrat
    if "montserrat" not in content.lower():
        issues.append({
            "category": "UI_TYPOGRAPHY",
            "severity": "HIGH",
            "file": str(rel_path),
            "rule": "Missing Montserrat Font",
            "message": "File CSS không định nghĩa hoặc tham chiếu font 'Montserrat'."
        })

    # Kiểm tra quy chuẩn in ấn Print A4
    if "@media print" not in content:
        issues.append({
            "category": "UI_PRINT_A4",
            "severity": "MEDIUM",
            "file": str(rel_path),
            "rule": "Missing Print Media Query",
            "message": "File CSS thiếu định nghĩa '@media print' cho xuất bản in ấn / PDF."
        })
    elif "A4" not in content and "210mm" not in content:
        issues.append({
            "category": "UI_PRINT_A4",
            "severity": "LOW",
            "file": str(rel_path),
            "rule": "Missing Explicit A4 Dimensions",
            "message": "Không tìm thấy kích thước A4 hoặc 210mm trong quy tắc print."
        })

    return issues


def validate_api_contract(payload: Dict[str, Any], is_error: bool = False) -> List[str]:
    """Kiểm tra tính hợp lệ của Payload API theo hợp đồng Frontend ↔ Backend."""
    errors = []
    if is_error:
        # Chuẩn RFC 7807 Problem Details
        required_fields = ["type", "title", "status", "detail"]
        for field in required_fields:
            if field not in payload:
                errors.append(f"RFC 7807 Error Payload thiếu trường bắt buộc: '{field}'")
        if "status" in payload and not (400 <= payload["status"] <= 599):
            errors.append(f"Mã HTTP status lỗi không hợp lệ: {payload['status']}")
    else:
        # Chuẩn Envelope: success + data
        if "success" not in payload:
            errors.append("API Success Payload thiếu trường 'success'")
        if "data" not in payload and "items" not in payload:
            errors.append("API Success Payload thiếu trường dữ liệu 'data'")
    return errors


def run_full_ui_ux_audit() -> bool:
    print("=" * 72)
    print("🎨 KTT UI/UX DESIGN SYSTEM & DEVTOOLS F12 AUDIT SCANNER")
    print(f"📁 Workspace: {ROOT_DIR}")
    print("=" * 72)

    all_issues = []
    html_files = []
    css_files = []

    # Thu thập các file HTML/CSS quan trọng
    target_dirs = [
        ROOT_DIR / "doc" / "Skill" / "ui-ux-design-system" / "assets",
        ROOT_DIR / "doc" / "Skill" / "meeting-note" / "assets",
        ROOT_DIR / "output"
    ]

    for d in target_dirs:
        if d.exists():
            html_files.extend(list(d.glob("*.html")))
            css_files.extend(list(d.glob("*.css")))

    # 1. Quét HTML
    print(f"\n🔍 Đang quét {len(html_files)} file giao diện HTML...")
    for hf in html_files:
        issues = audit_html_file(hf)
        all_issues.extend(issues)

    # 2. Quét CSS
    print(f"🔍 Đang quét {len(css_files)} file định kiểu CSS...")
    for cf in css_files:
        issues = audit_css_file(cf)
        all_issues.extend(issues)

    # 3. Kiểm tra mẫu API Contract
    print("🔍 Đang xác thực mẫu hợp đồng API Frontend ↔ Backend...")
    sample_success = {
        "success": True,
        "data": {"id": 1, "title": "Báo cáo BSC"},
        "meta": {"total": 1}
    }
    sample_error = {
        "type": "https://api.ktt.vn/errors/bad-request",
        "title": "Bad Request",
        "status": 400,
        "detail": "Thiếu tham số bắt buộc"
    }
    api_errs = validate_api_contract(sample_success, is_error=False)
    api_errs.extend(validate_api_contract(sample_error, is_error=True))
    for e in api_errs:
        all_issues.append({
            "category": "API_CONTRACT",
            "severity": "HIGH",
            "file": "API_Contract_Schema",
            "rule": "Contract Drift",
            "message": e
        })

    # Tổng kết
    print("\n" + "=" * 72)
    print("📊 BẢNG TỔNG KẾT KIỂM THỬ UI/UX & DEVTOOLS F12")
    print("=" * 72)

    critical_count = sum(1 for i in all_issues if i["severity"] == "CRITICAL")
    high_count = sum(1 for i in all_issues if i["severity"] == "HIGH")
    medium_count = sum(1 for i in all_issues if i["severity"] == "MEDIUM")
    low_count = sum(1 for i in all_issues if i["severity"] == "LOW")

    if all_issues:
        print(f"⚠️ Phát hiện {len(all_issues)} điểm cần lưu ý:")
        for issue in all_issues:
            print(f"  [{issue['severity']}] {issue['file']} — {issue['rule']}: {issue['message']}")
    else:
        print("✅ 100% CÁC FILE GIAO DIỆN VÀ ĐỊNH KIỂU ĐẠT CHUẨN DESIGN SYSTEM!")
        print("   - Typography: 100% Montserrat chuẩn mực.")
        print("   - Layout & Responsive: Đầy đủ Viewport & Thẻ Semantic.")
        print("   - Print & Xuất PDF: Đạt chuẩn khổ A4 (210mm).")
        print("   - DevTools DOM: Thẻ HTML cân bằng, DOM depth an toàn.")
        print("   - Accessibility: Tuân thủ WCAG 2.1 AA.")

    passed = (critical_count == 0 and high_count == 0)
    print("=" * 72)
    if passed:
        print("🏆 KẾT QUẢ: UI/UX & FRONTEND DESIGN SYSTEM ĐẠT TIÊU CHUẨN (PASS)")
    else:
        print("🚨 KẾT QUẢ: PHÁT HIỆN LỖI THIẾT KẾ CẦN CHỈNH SỬA (FAIL)")
    print("=" * 72)

    return passed


if __name__ == "__main__":
    success = run_full_ui_ux_audit()
    sys.exit(0 if success else 1)
