"""
dicom_analysis.py

Walks DICOM_GENERATION_OUTPUT/IMAGES/ recursively, runs your pylinac-based
analyzer on every .dcm file found, and writes results to a mirrored path
under DICOM_GENERATION_OUTPUT/ANALYSIS/.

Folder structure:
    DICOM_GENERATION_OUTPUT/
      IMAGES/
        Flatness/
          scan_001.dcm
        Field Size/
          scan_001.dcm
      ANALYSIS/
        Flatness/
          scan_001.txt
        Field Size/
          scan_001.txt

Usage (called from run_analysis in analysis_gui.py):
    from dicom_analysis import analyze_all

    analyze_all(output_dir=output_dir, status_callback=status_callback)
"""

from pathlib import Path
from metrics import run_analysis_on_path  # ← replace with your import


_GENERATION_ROOT = "DICOM_GENERATION_OUTPUT"
_IMAGES_DIR      = "IMAGES"
_ANALYSIS_DIR    = "ANALYSIS"


def analyze_all(
    output_dir: str | Path,
    status_callback: callable = print,
) -> None:
    """
    Find every .dcm file under DICOM_GENERATION_OUTPUT/IMAGES/ and write
    the analysis result string to the mirrored path under
    DICOM_GENERATION_OUTPUT/ANALYSIS/, replacing the .dcm extension with .txt.

    Args:
        output_dir:      Top-level directory chosen by the user in the GUI.
        status_callback: Callable that accepts a string — updates the GUI status bar.
    """
    base         = Path(output_dir)
    images_root  = base / _IMAGES_DIR
    analysis_root = base / _ANALYSIS_DIR

    if not images_root.exists():
        status_callback(f"⚠  Images folder not found: {images_root}")
        return

    dcm_files = sorted(images_root.rglob("*.dcm"))
    if not dcm_files:
        status_callback(f"⚠  No .dcm files found under {images_root}")
        return

    status_callback(f"Found {len(dcm_files)} DICOM file(s) — starting analysis…")

    errors = []
    for i, dcm_path in enumerate(dcm_files, start=1):
        # Preserve the subfolder structure (e.g. Flatness/scan_001.dcm)
        relative    = dcm_path.relative_to(images_root)
        output_path = (analysis_root / relative).with_suffix(".txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        status_callback(f"[{i}/{len(dcm_files)}] {relative}")

        try:
            result_str = run_analysis_on_path(dcm_path)  # ← your function here
            output_path.write_text(result_str, encoding="utf-8")
        except Exception as exc:
            msg = f"✖  Failed on {relative}: {exc}"
            status_callback(msg)
            errors.append(msg)

    if errors:
        status_callback(f"⚠  Analysis done with {len(errors)} error(s).")
    else:
        status_callback(f"✔  Analysis complete → {analysis_root}")
