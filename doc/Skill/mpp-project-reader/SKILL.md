---
name: mpp-project-reader
description: >
  Đọc, phân tích và báo cáo file Microsoft Project (.mpp). Dùng skill này bất cứ khi nào người dùng
  upload file .mpp hoặc nhắc đến "MS Project", "file project", "kế hoạch dự án .mpp", "tiến độ dự án",
  "Gantt chart", "WBS", "critical path", "resource allocation", "phân bổ nguồn lực", "ngân sách dự án",
  "xuất báo cáo dự án". Kể cả khi người dùng không nói rõ định dạng file, nếu họ hỏi về task, timeline,
  tỉ lệ hoàn thành, hay người phụ trách thì cũng nên dùng skill này nếu có file .mpp trong context.
  Skill này xử lý được file .mpp từ MS Project 2003 đến 2021.
---

# MPP Project Reader Skill

## Tổng quan

Skill này dùng thư viện **MPXJ** (Java-based, qua JPype) để đọc file `.mpp` từ Microsoft Project.
Hỗ trợ toàn bộ các tác vụ phân tích dự án: WBS, timeline, critical path, resource, cost, và xuất báo cáo.

> **BẢO MẬT & QUYỀN RIÊNG TƯ (STRICT PRIVACY)**: File kế hoạch dự án, chi phí, ngân sách và phân bổ nhân sự là tài sản bảo mật của doanh nghiệp. Tuyệt đối KHÔNG tự ý chia sẻ dữ liệu hoặc thông tin tài khoản cho bất kỳ AI Agent nào khác nếu chưa có sự xác nhận (CONFIRM) từ người dùng.

## Yêu cầu môi trường

- Python 3.x
- `mpxj` + `JPype1` (pip install mpxj JPype1 --break-system-packages)
- Java JVM (đã có sẵn trong môi trường Claude)

## Khởi tạo MPXJ (Bắt buộc dùng mỗi lần)

```python
import jpype
import os

def init_mpxj():
    """Khởi động JVM và trả về UniversalProjectReader class (hỗ trợ cả Windows & Linux)."""
    try:
        import mpxj
        mpxj_dir = os.path.join(os.path.dirname(mpxj.__file__), 'lib')
    except ImportError:
        mpxj_dir = os.path.join(sys.prefix, 'lib', 'site-packages', 'mpxj', 'lib')
    jars = [os.path.join(mpxj_dir, f) for f in os.listdir(mpxj_dir) if f.endswith('.jar')]
    classpath = os.pathsep.join(jars)
    
    if not jpype.isJVMStarted():
        jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={classpath}", convertStrings=False)
    
    return jpype.JClass('org.mpxj.reader.UniversalProjectReader')

def load_project(file_path):
    UPR = init_mpxj()
    reader = UPR()
    return reader.read(file_path)
```

> ⚠️ Package đúng là `org.mpxj` (KHÔNG phải `net.sf.mpxj`). Đây là phiên bản mới của thư viện.

---

## Các tác vụ và cách thực hiện

### 1. Hiển thị WBS & Danh sách Task

```python
project = load_project(file_path)
tasks = list(project.getTasks())

for task in tasks:
    if task.getID() is None:
        continue
    print(f"WBS={task.getWBS()} | {task.getName()} | %={task.getPercentageComplete()}")
```

**Trường dữ liệu quan trọng của Task:**

| Method | Ý nghĩa |
|--------|---------|
| `getID()` | ID task (None = summary root) |
| `getWBS()` | Mã WBS (vd: 1.2.3) |
| `getName()` | Tên task |
| `getStart()` | Ngày bắt đầu |
| `getFinish()` | Ngày kết thúc |
| `getDuration()` | Thời lượng (có đơn vị h/d) |
| `getPercentageComplete()` | % hoàn thành (float) |
| `getCritical()` | True nếu là critical path |
| `getMilestone()` | True nếu là milestone |
| `getCost()` | Chi phí thực tế |
| `getBaselineCost()` | Chi phí kế hoạch gốc |
| `getActualCost()` | Chi phí đã phát sinh |
| `getWork()` | Công việc (giờ công) |
| `getActualWork()` | Giờ công thực tế |
| `getOutlineLevel()` | Cấp độ phân cấp WBS |
| `getPredecessors()` | Danh sách task tiền nhiệm |
| `getNotes()` | Ghi chú |

---

### 2. Critical Path Analysis

```python
critical_tasks = [t for t in tasks if t.getCritical() and t.getID() is not None]

total_critical = len(critical_tasks)
print(f"Tổng task critical: {total_critical}")

for t in critical_tasks:
    print(f"  [{t.getWBS()}] {t.getName()} | {t.getStart()} → {t.getFinish()} | %={t.getPercentageComplete()}")
```

**Lưu ý phân tích:**
- Task critical = bất kỳ delay nào sẽ delay toàn bộ dự án
- Nếu `%Complete < 100` và `getCritical() == True` và `getFinish() < now` → **trễ deadline nghiêm trọng**
- So sánh với ngày hiện tại để phát hiện overdue tasks trên critical path

---

### 3. Timeline & Tiến độ Tổng quan

```python
from datetime import datetime, timezone

props = project.getProjectProperties()

project_start = props.getStartDate()
project_finish = props.getFinishDate()
status_date = props.getStatusDate()
author = props.getAuthor()

# Tính % hoàn thành tổng thể từ root task (ID=0)
root = tasks[0]  # Task summary toàn dự án
overall_pct = float(root.getPercentageComplete())

# Overdue tasks
now_str = str(datetime.now())
overdue = [t for t in tasks 
           if t.getID() and float(t.getPercentageComplete()) < 100 
           and str(t.getFinish()) < now_str]
```

---

### 4. Resource Allocation & Chi phí nhân sự

```python
resources = list(project.getResources())
assignments = list(project.getResourceAssignments())

for res in resources:
    if res.getID() == 0 or res.getName() is None:
        continue
    
    # Tổng assignment của resource này
    res_assignments = [a for a in assignments 
                      if a.getResource() and str(a.getResource().getID()) == str(res.getID())]
    
    total_work = sum(float(str(a.getWork()).replace('h','').strip()) 
                    for a in res_assignments if a.getWork())
    total_cost = sum(float(a.getCost()) for a in res_assignments if a.getCost())
    
    print(f"{res.getName()} | Rate={res.getStandardRate()} | Tasks={len(res_assignments)} | Work={total_work:.1f}h | Cost={total_cost:.2f}")
```

**Trường Resource:**

| Method | Ý nghĩa |
|--------|---------|
| `getName()` | Tên nhân sự/nhóm |
| `getType()` | WORK / MATERIAL / COST |
| `getStandardRate()` | Đơn giá chuẩn |
| `getCost()` | Tổng chi phí |
| `getWork()` | Tổng giờ công |
| `getMaxUnits()` | Công suất tối đa (%) |

---

### 5. Phân tích Chi phí Dự án

```python
# Chi phí theo từng task lớn (WBS cấp 1-2)
for task in tasks:
    if task.getID() is None:
        continue
    wbs = str(task.getWBS())
    level = wbs.count('.') + 1
    if level <= 2:  # Chỉ lấy summary level
        cost = float(task.getCost())
        baseline = float(task.getBaselineCost()) if task.getBaselineCost() else 0
        variance = cost - baseline
        print(f"[{wbs}] {task.getName()[:40]} | Cost={cost:.2f} | Baseline={baseline:.2f} | Variance={variance:+.2f}")
```

**Chỉ số chi phí quan trọng:**
- **Cost Variance (CV)** = Baseline Cost - Actual Cost → âm = vượt ngân sách
- **Cost Performance Index (CPI)** = Earned Value / Actual Cost
- Nếu BaselineCost = 0 trong file → dữ liệu baseline chưa được set trong MS Project

---

### 6. Xuất ra Excel

Đọc skill `xlsx` trước khi xuất Excel. Dưới đây là cấu trúc data để truyền vào:

```python
import openpyxl

wb = openpyxl.Workbook()

# Sheet 1: Task Summary
ws1 = wb.active
ws1.title = "Danh sách Task"
ws1.append(["WBS", "Tên Task", "Bắt đầu", "Kết thúc", "Thời lượng", "% Hoàn thành", "Chi phí", "Critical", "Ghi chú"])

for task in tasks:
    if task.getID() is None:
        continue
    ws1.append([
        str(task.getWBS()),
        str(task.getName()),
        str(task.getStart()),
        str(task.getFinish()),
        str(task.getDuration()),
        float(task.getPercentageComplete()),
        float(task.getCost()),
        bool(task.getCritical()),
        str(task.getNotes()) if task.getNotes() else ""
    ])

# Sheet 2: Resource
ws2 = wb.create_sheet("Resource")
ws2.append(["Tên", "Loại", "Đơn giá", "Tổng giờ công", "Tổng chi phí"])
for res in resources:
    if res.getID() == 0: continue
    ws2.append([str(res.getName()), str(res.getType()), str(res.getStandardRate()),
                str(res.getWork()), float(res.getCost())])

wb.save('/mnt/user-data/outputs/project_report.xlsx')
```

---

### 7. Xuất Word/PDF (Báo cáo tổng kết dự án)

Đọc skill `docx` và `pdf` trước. Cấu trúc báo cáo đề xuất:

```
1. Thông tin tổng quan dự án
   - Tên, tác giả, ngày bắt đầu/kết thúc, % hoàn thành tổng thể
2. Tóm tắt tiến độ
   - Số task tổng / hoàn thành / đang chạy / trễ hạn
   - Critical path overview
3. Phân tích chi phí
   - Tổng chi phí, phân bổ theo nhóm
4. Phân bổ Resource
   - Bảng giờ công + chi phí từng người
5. Rủi ro & Khuyến nghị
   - Task critical chưa hoàn thành
   - Task overdue
```

---

### 8. Final Project Evaluation (Đánh giá kết thúc dự án)

```python
# Tính các KPI đánh giá dự án
total_tasks = [t for t in tasks if t.getID() is not None and not t.getMilestone()]
completed = [t for t in total_tasks if float(t.getPercentageComplete()) == 100]
in_progress = [t for t in total_tasks if 0 < float(t.getPercentageComplete()) < 100]
not_started = [t for t in total_tasks if float(t.getPercentageComplete()) == 0]

completion_rate = len(completed) / len(total_tasks) * 100 if total_tasks else 0

# Schedule Performance
from datetime import datetime
now = datetime.now()

late_tasks = []
for t in total_tasks:
    finish_str = str(t.getFinish())
    if finish_str and finish_str < str(now) and float(t.getPercentageComplete()) < 100:
        late_tasks.append(t)

# Cost summary
total_cost = sum(float(t.getCost()) for t in total_tasks)
total_baseline = sum(float(t.getBaselineCost()) for t in total_tasks)

print(f"=== KẾT QUẢ DỰ ÁN ===")
print(f"Tổng task: {len(total_tasks)}")
print(f"Hoàn thành: {len(completed)} ({completion_rate:.1f}%)")
print(f"Đang thực hiện: {len(in_progress)}")
print(f"Chưa bắt đầu: {len(not_started)}")
print(f"Trễ hạn: {len(late_tasks)}")
print(f"Tổng chi phí: {total_cost:,.2f}")
print(f"Ngân sách gốc: {total_baseline:,.2f}")
```

---

## Lưu ý quan trọng

1. **Encoding tiếng Việt**: Khi `convertStrings=False` (JPype mặc định), phải dùng `str(task.getName())` để convert JString → Python str. Nếu không sẽ bị lỗi hiển thị.

2. **Root task (ID=0)**: MS Project có một task ảo ở ID=0 là summary toàn dự án. Bỏ qua khi đếm task thực, nhưng dùng để lấy `getPercentageComplete()` tổng thể.

3. **Duration units**: `getDuration()` trả về `Duration` object của MPXJ. Dùng `str()` để lấy chuỗi như "2.0h" hay "40.0d". Dùng `task.getDuration().getDuration()` để lấy số thuần.

4. **Cost = 0**: Nếu nhiều task có Cost = 0, khả năng cao file MPP không set rate cho resource. Cần kết hợp với file ngân sách Excel riêng (như `NGAN_SACH_DU_AN.xlsx`).

5. **JVM chỉ khởi động một lần**: Kiểm tra `jpype.isJVMStarted()` trước khi gọi `startJVM()`.

6. **Dependency/Predecessors**: `task.getPredecessors()` trả về list `Relation` objects. Dùng `relation.getTargetTask().getID()` để lấy ID task tiền nhiệm.

---

## Scripts có sẵn

Xem thư mục `scripts/` để biết các script tái sử dụng:
- `scripts/read_mpp.py` — Helper đọc file và trả về dict chuẩn hóa
- `scripts/export_excel.py` — Xuất toàn bộ data ra Excel multi-sheet
- `scripts/project_summary.py` — In báo cáo tóm tắt ra console

---

## Ví dụ output nhanh (Quick Summary)

Khi người dùng chỉ muốn xem tổng quan nhanh, dùng pattern này:

```python
project = load_project(file_path)
tasks = list(project.getTasks())
props = project.getProjectProperties()
resources = list(project.getResources())

root = tasks[0]
real_tasks = [t for t in tasks if t.getID() is not None and t.getID() != 0]
completed = sum(1 for t in real_tasks if float(t.getPercentageComplete()) == 100)
critical = [t for t in real_tasks if t.getCritical()]

print(f"""
📁 DỰ ÁN: {props.getAuthor()} — {props.getStartDate()} → {props.getFinishDate()}
📊 Tiến độ tổng thể: {float(root.getPercentageComplete()):.0f}%
✅ Task hoàn thành: {completed}/{len(real_tasks)}
⚠️  Critical Path: {len(critical)} tasks
👥 Resources: {len([r for r in resources if r.getID() != 0])} người/nhóm
💰 Tổng chi phí: {sum(float(t.getCost()) for t in real_tasks):,.0f}
""")
```
