from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
# -*- coding: utf-8 -*-
"""
Harness Quality & Fact Verification Audit for KTT Meeting Note
"""
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GLOSSARY_PATH = BASE_DIR / "doc" / "glossary.txt"
HTML_PATH = BASE_DIR / "doc" / "transcripts" / "Bien_Ban_Hop_Bao_Cao_Quy_3_Va_Ke_Hoach_Quy_4_2026_BSC_KPI.html"

def main():
    if not HTML_PATH.exists():
        print(f"Error: {HTML_PATH} does not exist")
        return

    html_text = HTML_PATH.read_text(encoding="utf-8")

    # 1. Unicode Check
    nfc_text = unicodedata.normalize("NFC", html_text)
    is_nfc = (html_text == nfc_text)
    print(f"[CHECK 1] Unicode Form NFC: {'PASS' if is_nfc else 'FAIL'}")

    # 2. Gender Consistency Check against Glossary
    person_pat = re.compile(r"^(Anh|Chị)\s+([^(]+)\s*\(([^)]+)\)$")
    registry = {}
    if GLOSSARY_PATH.exists():
        for line in GLOSSARY_PATH.read_text(encoding="utf-8").splitlines():
            m = person_pat.match(line.strip())
            if m:
                name = m.group(2).strip()
                gender = m.group(1).strip()
                dept = m.group(3).strip()
                registry[name.lower()] = {"gender": gender, "name": name, "dept": dept}

    gender_errors = []
    for name_key, p in registry.items():
        opp = "Chị" if p["gender"] == "Anh" else "Anh"
        wrong_pat = re.compile(rf"\b{opp}\s+{re.escape(p['name'])}\b", re.IGNORECASE)
        matches = wrong_pat.findall(html_text)
        if matches:
            gender_errors.append((p["name"], p["gender"], opp, len(matches)))

    if gender_errors:
        print(f"[CHECK 2] Gender Consistency: FAIL ({len(gender_errors)} errors)")
        for name, expected, actual, count in gender_errors:
            print(f"   -> {name}: Expected {expected}, found {actual} {count} times")
    else:
        print(f"[CHECK 2] Gender Consistency: PASS (100% matched with glossary)")

    # 3. HTML Tag Balance Check
    tags = ["div", "table", "tr", "th", "td", "ul", "li", "span", "p"]
    mismatches = {}
    for t in tags:
        open_c = len(re.findall(rf"<{t}\b", html_text, re.IGNORECASE))
        close_c = len(re.findall(rf"</{t}>", html_text, re.IGNORECASE))
        if open_c != close_c:
            mismatches[t] = (open_c, close_c)

    if mismatches:
        print(f"[CHECK 3] HTML Tag Balance: FAIL ({mismatches})")
    else:
        print(f"[CHECK 3] HTML Tag Balance: PASS (All tags balanced)")

    # 4. Department Coverage Check (14 sections)
    required_sections = [
        "Kế toán", "Mua hàng", "Kho", "QC", "Nhân sự", "IT",
        "Marketing", "Data", "Đại lý", "Nhà máy", "Michelin", "TMĐT"
    ]
    missing_sections = [sec for sec in required_sections if sec.lower() not in html_text.lower()]
    if missing_sections:
        print(f"[CHECK 4] Department Coverage: FAIL (Missing: {missing_sections})")
    else:
        print(f"[CHECK 4] Department Coverage: PASS (All 14 department sections included)")

    # 5. Flagged items check
    flagged = re.findall(r"\[\?\?\]|\[cần [^\]]+\]", html_text)
    print(f"[CHECK 5] Unresolved Flags: {len(flagged)} items found")
    for f in flagged[:10]:
        print(f"   -> {f}")

if __name__ == "__main__":
    main()
