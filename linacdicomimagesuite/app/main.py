from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from linacdicomimagesuite.app.analysis_gui import AnalysisGUI
else:
    from .analysis_gui import AnalysisGUI

if __name__ == "__main__":
    app = AnalysisGUI()
    app.mainloop()
