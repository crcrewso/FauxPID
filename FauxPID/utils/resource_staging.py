from pathlib import Path
import shutil
import sys


def _resolve_resources_dir() -> Path:
    candidates: list[Path] = []

    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "resources")
        bundle_dir = getattr(sys, "_MEIPASS", None)
        if bundle_dir:
            candidates.append(Path(bundle_dir) / "resources")

    candidates.append(Path(__file__).resolve().parents[2] / "resources")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


RESOURCES_DIR = _resolve_resources_dir()


def _copy_entry(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    elif source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def stage_resources_for_image_type(output_root: Path, image_type_name: str) -> None:
    """Copy shared resources and the matching image-type folder into an output tree."""
    output_root.mkdir(parents=True, exist_ok=True)

    if RESOURCES_DIR.exists():
        for entry in RESOURCES_DIR.iterdir():
            if entry.is_file():
                _copy_entry(entry, output_root / entry.name)

        image_type_resource_dir = RESOURCES_DIR / image_type_name
        if image_type_resource_dir.exists():
            output_dir = Path(output_root / image_type_name)
            output_dir.mkdir(parents=True, exist_ok=True)
            _copy_entry(image_type_resource_dir, output_dir)