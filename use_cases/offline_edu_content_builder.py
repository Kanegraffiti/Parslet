"""Use case: build offline education content bundles.
Collects .txt, .png and .mp3 files from a source directory and
packages them into a clean folder under ``Parslet_Results``. A
manifest.json lists all included files.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from parslet.core import parslet_task, ParsletFuture, DAG, DAGRunner
from parslet.utils.resource_utils import get_available_ram_mb, get_battery_level

logger = logging.getLogger(__name__)


@parslet_task
def create_output_dir(base: str | None = None) -> Path:
    base_path = Path(base or "Parslet_Results")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out = base_path / timestamp
    out.mkdir(parents=True, exist_ok=True)
    return out


@parslet_task
def check_resources(
    min_ram_mb: int = 50, min_battery: int = 20
) -> Dict[str, int | float | None | bool]:
    ram = get_available_ram_mb()
    batt = get_battery_level()
    ram_ok = ram is None or ram >= min_ram_mb
    batt_ok = batt is None or batt >= min_battery
    return {
        "ram": ram,
        "battery": batt,
        "ram_ok": ram_ok,
        "battery_ok": batt_ok,
        "proceed": ram_ok and batt_ok,
    }


@parslet_task
def gather_files(src: str, resources: Dict[str, bool]) -> List[Path] | None:
    if not resources.get("proceed", True):
        return None
    src_path = Path(src)
    files = list(src_path.glob("**/*"))
    return [p for p in files if p.suffix.lower() in {".txt", ".png", ".mp3"}]


@parslet_task
def sanitize_filenames(files: List[Path] | None) -> List[Path] | None:
    if files is None:
        return None
    sanitized: List[Path] = []
    for p in files:
        new_name = p.name.replace(" ", "_")
        sanitized.append(p.with_name(new_name))
    return sanitized


@parslet_task
def copy_files(files: List[Path] | None, dest: Path) -> List[str]:
    copied: List[str] = []
    if files is None:
        return copied
    dest.mkdir(parents=True, exist_ok=True)
    for src in files:
        target = dest / src.name.replace(" ", "_")
        try:
            shutil.copy2(src, target)
            copied.append(target.name)
        except Exception as e:
            logger.error("Failed to copy %s: %s", src, e)
    return copied


@parslet_task
def write_manifest(
    file_names: List[str], dest: Path, resources: Dict[str, bool]
) -> str:
    manifest_path = dest / "manifest.json"
    log_path = dest / "diagnostics.log"
    logging.basicConfig(filename=log_path, level=logging.INFO)
    manifest = {"files": file_names, "resources": resources}
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logging.info("Manifest written")
    return str(manifest_path)


def main(src: str = "./content") -> List[ParsletFuture]:
    out_dir_f = create_output_dir()
    res_f = check_resources()
    files_f = gather_files(src, res_f)
    clean_f = sanitize_filenames(files_f)
    copied_f = copy_files(clean_f, out_dir_f)
    manifest_f = write_manifest(copied_f, out_dir_f, res_f)
    return [manifest_f]


if __name__ == "__main__":
    dag = DAG(main())
    runner = DAGRunner(dag)
    runner.run()
