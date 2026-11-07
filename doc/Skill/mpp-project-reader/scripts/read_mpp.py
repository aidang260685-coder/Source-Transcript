"""
read_mpp.py — Helper chuẩn hóa đọc file .mpp và trả về dict Python thuần.
Dùng: from scripts.read_mpp import load_project_data
"""

import jpype
import os
from datetime import datetime


def init_mpxj():
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


def _str(val):
    """Safe convert JString → Python str."""
    return str(val) if val is not None else ''


def _float(val):
    """Safe convert to float."""
    try:
        return float(val) if val is not None else 0.0
    except:
        return 0.0


def _bool(val):
    return bool(val) if val is not None else False


def load_project_data(file_path: str) -> dict:
    """
    Đọc file .mpp và trả về dict chuẩn hóa:
    {
        'info': {...},
        'tasks': [...],
        'resources': [...],
        'assignments': [...],
        'summary': {...}
    }
    """
    UPR = init_mpxj()
    reader = UPR()
    project = reader.read(file_path)
    
    props = project.getProjectProperties()
    all_tasks = list(project.getTasks())
    all_resources = list(project.getResources())
    all_assignments = list(project.getResourceAssignments())
    
    # Project info
    info = {
        'author': _str(props.getAuthor()),
        'start': _str(props.getStartDate()),
        'finish': _str(props.getFinishDate()),
        'status_date': _str(props.getStatusDate()),
        'currency': _str(props.getCurrencySymbol()),
        'overall_pct': _float(all_tasks[0].getPercentageComplete()) if all_tasks else 0.0
    }
    
    # Tasks
    tasks = []
    for t in all_tasks:
        if t.getID() is None:
            continue
        tasks.append({
            'id': int(t.getID()),
            'wbs': _str(t.getWBS()),
            'name': _str(t.getName()),
            'start': _str(t.getStart()),
            'finish': _str(t.getFinish()),
            'duration_str': _str(t.getDuration()),
            'duration_val': _float(t.getDuration().getDuration()) if t.getDuration() else 0.0,
            'pct_complete': _float(t.getPercentageComplete()),
            'cost': _float(t.getCost()),
            'baseline_cost': _float(t.getBaselineCost()),
            'actual_cost': _float(t.getActualCost()),
            'work_str': _str(t.getWork()),
            'is_critical': _bool(t.getCritical()),
            'is_milestone': _bool(t.getMilestone()),
            'is_summary': _bool(t.getSummary()),
            'outline_level': int(t.getOutlineLevel()) if t.getOutlineLevel() else 0,
            'notes': _str(t.getNotes()),
        })
    
    # Resources
    resources = []
    for r in all_resources:
        if r.getID() == 0 or r.getName() is None:
            continue
        resources.append({
            'id': int(r.getID()),
            'name': _str(r.getName()),
            'type': _str(r.getType()),
            'std_rate': _str(r.getStandardRate()),
            'cost': _float(r.getCost()),
            'work_str': _str(r.getWork()),
        })
    
    # Assignments
    assignments = []
    for a in all_assignments:
        task = a.getTask()
        res = a.getResource()
        assignments.append({
            'task_id': int(task.getID()) if task and task.getID() is not None else None,
            'task_name': _str(task.getName()) if task else '',
            'resource_id': int(res.getID()) if res and res.getID() is not None else None,
            'resource_name': _str(res.getName()) if res else '',
            'units': _float(a.getUnits()),
            'cost': _float(a.getCost()),
            'work_str': _str(a.getWork()),
        })
    
    # Summary stats
    real_tasks = [t for t in tasks if t['id'] != 0 and not t['is_summary']]
    now_str = datetime.now().isoformat()
    
    summary = {
        'total_tasks': len(real_tasks),
        'completed': sum(1 for t in real_tasks if t['pct_complete'] == 100),
        'in_progress': sum(1 for t in real_tasks if 0 < t['pct_complete'] < 100),
        'not_started': sum(1 for t in real_tasks if t['pct_complete'] == 0),
        'critical_count': sum(1 for t in real_tasks if t['is_critical']),
        'overdue': sum(1 for t in real_tasks if t['finish'] < now_str and t['pct_complete'] < 100),
        'total_cost': sum(t['cost'] for t in real_tasks),
        'total_baseline': sum(t['baseline_cost'] for t in real_tasks),
        'resource_count': len(resources),
    }
    summary['cost_variance'] = summary['total_baseline'] - summary['total_cost']
    
    return {
        'info': info,
        'tasks': tasks,
        'resources': resources,
        'assignments': assignments,
        'summary': summary
    }
