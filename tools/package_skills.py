import os
import zipfile
from pathlib import Path

skills_dir = Path(__file__).resolve().parent.parent / "doc" / "Skill"

for skill_folder in sorted(skills_dir.iterdir()):
    if skill_folder.is_dir():
        skill_name = skill_folder.name
        skill_archive = skills_dir / f"{skill_name}.skill"
        print(f"Packaging {skill_name} -> {skill_archive.name}...")
        
        with zipfile.ZipFile(skill_archive, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_folder):
                # skip pycache
                dirs[:] = [d for d in dirs if d not in {"__pycache__", ".pytest_cache"}]
                for file in files:
                    if file.endswith((".pyc", ".pyo")):
                        continue
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(skills_dir)
                    zf.write(full_path, rel_path)
        print(f"  OK ({skill_archive.stat().st_size:,} bytes)")
