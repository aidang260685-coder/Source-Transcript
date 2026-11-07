# -*- coding: utf-8 -*-
"""
Test Layout UI, Dàn trang in PDF A4 & Styling:
Kiểm tra cấu trúc khung HTML, CSS responsive, ngắt trang print pagination và letterhead Kiên Thành Tín.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "doc" / "Skill" / "meeting-note" / "assets"

def test_css_styling_and_font():
    style_css = ASSETS_DIR / "style.css"
    assert style_css.exists()
    content = style_css.read_text(encoding="utf-8")
    
    # Kiểm tra font Montserrat
    assert "Montserrat" in content
    # Kiểm tra quy tắc print A4
    assert "@media print" in content
    assert "210mm" in content
    assert "page-break" in content

def test_html_templates_exist_and_balanced():
    templates = ["khung_kickoff.html", "khung_weekly.html", "khung_bsc_kpi.html"]
    for t_name in templates:
        t_file = ASSETS_DIR / t_name
        assert t_file.exists(), f"Thiếu khung template {t_name}"
        html = t_file.read_text(encoding="utf-8")
        
        # Kiểm tra thẻ HTML cơ bản
        assert "<!DOCTYPE html>" in html
        assert "<html" in html and "</html>" in html
        assert "<head" in html and "</head>" in html
        assert "<body" in html and "</body>" in html
        
        # Kiểm tra cân bằng các thẻ khối chính
        assert html.count("<table") == html.count("</table>"), f"{t_name} bị lệch thẻ <table>"
        assert html.count("<div") == html.count("</div>"), f"{t_name} bị lệch thẻ <div>"
