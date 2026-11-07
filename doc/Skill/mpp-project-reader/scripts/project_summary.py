"""
project_summary.py — In báo cáo tóm tắt nhanh ra console.
Dùng: python scripts/project_summary.py <path_to.mpp>
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.read_mpp import load_project_data


def print_summary(file_path: str):
    data = load_project_data(file_path)
    info = data['info']
    s = data['summary']
    tasks = data['tasks']
    resources = data['resources']

    print("=" * 60)
    print("📁  BÁO CÁO DỰ ÁN MS PROJECT")
    print("=" * 60)
    print(f"  Tác giả      : {info['author']}")
    print(f"  Bắt đầu      : {info['start']}")
    print(f"  Kết thúc     : {info['finish']}")
    print(f"  Status Date  : {info['status_date']}")
    print(f"  Tiến độ tổng : {info['overall_pct']:.0f}%")
    print()

    print("📊  TIẾN ĐỘ TASK")
    print(f"  Tổng task       : {s['total_tasks']}")
    print(f"  ✅ Hoàn thành   : {s['completed']}")
    print(f"  🔄 Đang thực hiện: {s['in_progress']}")
    print(f"  ⏸  Chưa bắt đầu : {s['not_started']}")
    print(f"  ⚠️  Trễ hạn      : {s['overdue']}")
    print(f"  🔴 Critical Path : {s['critical_count']} tasks")
    print()

    print("💰  CHI PHÍ")
    print(f"  Tổng chi phí    : {s['total_cost']:>12,.2f} {info['currency']}")
    print(f"  Ngân sách gốc   : {s['total_baseline']:>12,.2f} {info['currency']}")
    variance = s['cost_variance']
    sign = "✅" if variance >= 0 else "❌"
    print(f"  Variance (B-A)  : {sign} {variance:>+12,.2f} {info['currency']}")
    print()

    print("👥  RESOURCES")
    for r in resources[:10]:
        print(f"  {r['name'][:30]:30s} | {r['std_rate']:15s} | Cost: {r['cost']:>10,.2f}")
    print()

    print("⚠️   CRITICAL PATH (chưa hoàn thành)")
    critical_incomplete = [t for t in tasks if t['is_critical'] and t['pct_complete'] < 100 and t['id'] != 0]
    if not critical_incomplete:
        print("  ✅ Tất cả critical tasks đã hoàn thành!")
    for t in critical_incomplete:
        print(f"  [{t['wbs']:10s}] {t['name'][:40]:40s} | {t['pct_complete']:5.0f}% | {t['finish'][:10]}")

    print()
    print("=" * 60)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/project_summary.py <path.mpp>")
        sys.exit(1)
    print_summary(sys.argv[1])
