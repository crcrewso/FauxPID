"""
analysis_gui.py

A reusable tkinter GUI for image generation and analysis options.
Customize the ANALYSIS_OPTIONS and OTHER_OPTIONS lists to match your needs,
then wire up the `run_analysis` function at the bottom to call your main logic.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading
from pathlib import Path
import tomllib
import json
from datetime import datetime
from dicom_analysis import analyze_all
from create_image import ImageGenerator


# ── Customize your options here ──────────────────────────────────────────────

IMAGE_TYPE_OPTIONS = [
    "Artifacts",
    "Field Size",
    "Flatness",
    "Symmetry",
    "Orthogonality",
    "CAX Offset",
]

OTHER_OPTIONS = [
    "Run analysis on generated images",
    "Include PNG with each DICOM",
    "Results as JSON (default is .txt)",
]

DEFAULT_IMAGE_TYPE_OPTIONS = [
    "Artifacts",
    "Field Size",
    "Flatness",
    "Symmetry",
    "CAX Offset",
]

DEFAULT_OTHER_OPTIONS = [
    "Include PNG with each DICOM",
    "Results as JSON (default is .txt)",
]

# ─────────────────────────────────────────────────────────────────────────────


def _load_project_version() -> str:
    pyproject_path = Path(__file__).with_name("pyproject.toml")
    try:
        with pyproject_path.open("rb") as pyproject_file:
            project_data = tomllib.load(pyproject_file)
        return project_data["project"]["version"]
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "0.0.0"


PROJECT_VERSION = _load_project_version()
SETTINGS_DIRNAME = ".linacdicomimagesuite"
SETTINGS_FILENAME = "analysis_gui_settings.toml"


class AnalysisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"DICOM Image Generator v{PROJECT_VERSION}")
        self.resizable(False, False)
        self.configure(bg="#e0e0f0")

        self._build_styles()
        self._build_ui()
        self._apply_settings(self._load_settings())
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Styles ────────────────────────────────────────────────────────────────

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Card.TFrame",
            background="#e0e0f0",
            relief="flat",
        )
        style.configure(
            "TLabel",
            background="#e0e0f0",
            foreground="#16213e",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Header.TLabel",
            background="#ffffff",
            foreground="#000000",
            font=("Segoe UI", 13, "bold"),
        )
        style.configure(
            "Section.TLabel",
            #background="#A3CFFA",
            foreground="#000000",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "TCheckbutton",
            background="#e0e0f0",
            foreground="#000000",
            font=("Segoe UI", 10),
            focuscolor="#ffffff",
        )
        style.map(
            "TCheckbutton",
            # background=[("active", "#e0e0f0")],
            foreground=[("active", "#4AA3FF")],
        )
        style.configure(
            "Run.TButton",
            background="#4AA3FF",
            foreground="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padding=(12, 8),
        )
        style.map(
            "Run.TButton",
            background=[("active", "#4AA3FF"), ("disabled", "#555577")],
            foreground=[("disabled", "#aaaaaa")],
        )
        style.configure(
            "TProgressbar",
            troughcolor="#0f3460",
            background="#4AA3FF",
            thickness=6,
        )
        style.configure(
            "TEntry",
            fieldbackground="#ffffff",
            foreground="#000000",
            insertcolor="#193857",
            font=("Segoe UI", 10),
            relief="flat",
        )
        style.configure(
            "Browse.TButton",
            background="#4AA3FF",
            foreground="#ffffff",
            font=("Segoe UI", 9),
            relief="flat",
            padding=(6, 4),
        )
        style.map(
            "Browse.TButton",
            background=[("active", "#1a4080")],
            foreground=[("active", "#e0e0f0")],
        )

    # ── UI Layout ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = tk.Frame(self, bg="#FAFAFA", padx=20, pady=20)
        outer.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            outer,
            text=f"DICOM Image Generator v{PROJECT_VERSION}",
            style="Header.TLabel",
        ).pack(
            anchor="w", pady=(0, 16)
        )

        # ── Output folder ─────────────────────────────────────────────────────
        folder_card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        folder_card.pack(fill="x", pady=(0, 10))

        ttk.Label(folder_card, text="OUTPUT DIRECTORY", style="Section.TLabel").pack(
            anchor="w", pady=(0, 6)
        )

        path_row = tk.Frame(folder_card, bg="#e0e0f0")
        path_row.pack(fill="x")

        self.folder_var = tk.StringVar(value="")
        path_entry = ttk.Entry(path_row, textvariable=self.folder_var, width=44)
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Button(
            path_row,
            text="Browse…",
            style="Browse.TButton",
            command=self._browse_folder,
        ).pack(side="left")

        # ── IMAGE_TYPE options ──────────────────────────────────────────────────
        image_type_card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        image_type_card.pack(fill="x", pady=(0, 10))

        ttk.Label(
            image_type_card, text="IMAGE TYPE OPTIONS", style="Section.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        self.image_type_vars = {}
        col_frame = tk.Frame(image_type_card, bg="#e0e0f0")
        col_frame.pack(fill="x")

        mid = (len(IMAGE_TYPE_OPTIONS) + 1) // 2
        for i, opt in enumerate(IMAGE_TYPE_OPTIONS):
            var = tk.BooleanVar(value=True)
            self.image_type_vars[opt] = var
            col = 0 if i < mid else 1
            row = i if i < mid else i - mid
            cb = ttk.Checkbutton(col_frame, text=opt, variable=var)
            cb.grid(row=row, column=col, sticky="w", padx=(0, 24), pady=2)

        # ── Other options ───────────────────────────────────────────────────
        other_card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        other_card.pack(fill="x", pady=(0, 10))

        ttk.Label(
            other_card, text="OTHER OPTIONS", style="Section.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        self.other_vars = {}
        for opt in OTHER_OPTIONS:
            var = tk.BooleanVar(value=True)
            self.other_vars[opt] = var
            ttk.Checkbutton(other_card, text=opt, variable=var).pack(
                anchor="w", pady=2
            )

        # ── Run + status ──────────────────────────────────────────────────────
        run_frame = tk.Frame(outer, bg="#e0e0f0")
        run_frame.pack(fill="x", pady=(10, 0))

        self.run_btn = ttk.Button(
            run_frame,
            text="▶  GENERATE",
            style="Run.TButton",
            command=self._on_run,
        )
        self.run_btn.pack(fill="x", pady=(0, 8))

        self.progress = ttk.Progressbar(
            run_frame, mode="determinate", style="TProgressbar"
        )
        self.progress.pack(fill="x", pady=(0, 6))

        self.status_var = tk.StringVar(value="Ready.")
        status_label = tk.Label(
            run_frame,
            textvariable=self.status_var,
            bg="#B3B3EB",
            fg="#1a1a2e",
            font=("Segoe UI", 9),
            anchor="w",
        )
        status_label.pack(fill="x")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select output directory")
        if folder:
            self.folder_var.set(folder)

    def _settings_path(self) -> Path:
        return Path.home() / SETTINGS_DIRNAME / SETTINGS_FILENAME

    def _default_settings(self) -> dict[str, object]:
        return {
            "output_dir": "",
            "image_type_options": list(DEFAULT_IMAGE_TYPE_OPTIONS),
            "other_options": list(DEFAULT_OTHER_OPTIONS),
            "last_updated": datetime.now().isoformat(),
        }

    def _load_settings(self) -> dict[str, object]:
        settings_path = self._settings_path()
        defaults = self._default_settings()

        if not settings_path.exists():
            self._save_settings(defaults)
            return defaults

        try:
            with settings_path.open("rb") as settings_file:
                loaded_settings = tomllib.load(settings_file)
        except (OSError, tomllib.TOMLDecodeError):
            self._save_settings(defaults)
            return defaults

        if not isinstance(loaded_settings, dict):
            self._save_settings(defaults)
            return defaults

        image_type_options = [
            option
            for option in loaded_settings.get("image_type_options", defaults["image_type_options"])
            if option in IMAGE_TYPE_OPTIONS
        ]
        other_options = [
            option
            for option in loaded_settings.get("other_options", defaults["other_options"])
            if option in OTHER_OPTIONS
        ]

        if not image_type_options:
            image_type_options = list(IMAGE_TYPE_OPTIONS)
        if not other_options:
            other_options = list(OTHER_OPTIONS)

        return {
            "output_dir": str(loaded_settings.get("output_dir", "")),
            "image_type_options": image_type_options,
            "other_options": other_options,
        }

    def _save_settings(self, settings: dict[str, object] | None = None) -> None:
        settings = settings or self._collect_settings()
        settings_path = self._settings_path()
        try:
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            settings_path.write_text(self._format_toml_settings(settings), encoding="utf-8")
        except OSError:
            pass

    def _format_toml_settings(self, settings: dict[str, object]) -> str:
        def format_string(value: object) -> str:
            return json.dumps(str(value), ensure_ascii=False)

        def format_string_list(values: object) -> str:
            items = [format_string(value) for value in values if value is not None]
            return "[" + ", ".join(items) + "]"

        output_dir = format_string(settings.get("output_dir", ""))
        image_type_options = format_string_list(settings.get("image_type_options", []))
        other_options = format_string_list(settings.get("other_options", []))
        last_updated = format_string(settings.get("last_updated", datetime.now().isoformat()))

        return (
            "output_dir = " + output_dir + "\n"
            + "image_type_options = " + image_type_options + "\n"
            + "other_options = " + other_options + "\n"
            + "last_updated = " + last_updated + "\n"
        )

    def _collect_settings(self) -> dict[str, object]:
        return {
            "output_dir": self.folder_var.get(),
            "image_type_options": [
                option for option, variable in self.image_type_vars.items() if variable.get()
            ],
            "other_options": [
                option for option, variable in self.other_vars.items() if variable.get()
            ],
            "last_updated": datetime.now().isoformat(),
        }

    def _apply_settings(self, settings: dict[str, object]) -> None:
        self.folder_var.set(str(settings.get("output_dir", "")))

        selected_image_types = set(settings.get("image_type_options", []))
        for option, variable in self.image_type_vars.items():
            variable.set(option in selected_image_types)

        selected_other_options = set(settings.get("other_options", []))
        for option, variable in self.other_vars.items():
            variable.set(option in selected_other_options)

    def _on_close(self):
        self._save_settings()
        self.destroy()

    def _on_run(self):
        """Validate inputs, then run analysis in a background thread."""
        if not self.folder_var.get():
            self._set_status("⚠  Please select an output directory first.", error=True)
            return

        chosen_image_type = [k for k, v in self.image_type_vars.items() if v.get()]
        chosen_other = [k for k, v in self.other_vars.items() if v.get()]

        self._save_settings()

        self.run_btn.configure(state="disabled")
        self.progress.start(12)
        self._set_status("Running…")

        def worker():
            try:
                run_analysis(
                    output_dir=self.folder_var.get(),
                    image_type_options=chosen_image_type,
                    other_options=chosen_other,
                    status_callback=self._set_status,
                )
                self.after(0, lambda: self._set_status("✔  Done!"))
            except Exception as e:
                self.after(0, lambda: self._set_status(f"✖  Error: {repr(e)}", error=True))
            finally:
                self.after(0, self._on_done)

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self):
        self.progress.stop()
        self.run_btn.configure(state="normal")

    def _set_status(self, msg, error=False):
        color = "#e94560" if error else "#606080"
        self.status_var.set(msg)
        # Update label color by re-querying the widget
        for widget in self.winfo_children():
            pass  # label colour set via StringVar; extend here if needed


# ── YOUR LOGIC GOES HERE ──────────────────────────────────────────────────────

def run_analysis(output_dir, image_type_options, other_options, status_callback):
    """
    Calls image generation and analysis functions based on the user's selections in the GUI.
    Args:
        output_dir      (str):       Folder path chosen by the user.
        image_type_options (list[str]): Names of checked image type options.
        other_options  (list[str]): Names of checked other options.
        status_callback  (callable):  Call status_callback("message") to update
                                      the status bar from your worker thread.
    """
    if "Run analysis on generated images" in other_options:
        run_analysis_on_generated = True
    else:
        run_analysis_on_generated = False
    if "Include PNG with each DICOM" in other_options:
        include_png = True
    else:
        include_png = False
    if "Results as JSON (default is .txt)" in other_options:
        results_as_json = "json"
    else:
        results_as_json = "txt"

    status_callback("Folder setting up")
    output_gen_dir = Path(output_dir) / "DICOM_GENERATION_OUTPUT"
    images_dir = output_gen_dir / "Images"
    image_generator = ImageGenerator(file_out_directory=images_dir, include_png=include_png)
    if "Artifacts" in image_type_options:
        status_callback("Generating Artifacts images…")
        image_generator.generate_artifacts_images()
    if "Field Size" in image_type_options:
        status_callback("Generating Field Size images…")
        image_generator.generate_field_size_images()
    if "Flatness" in image_type_options:
        status_callback("Generating Flatness images…")
        image_generator.generate_flatness_images()
    if "Symmetry" in image_type_options:
        status_callback("Generating Symmetry images…")
        image_generator.generate_symmetry_images()
    if "CAX Offset" in image_type_options:
        status_callback("Generating CAX Offset images…")
        image_generator.generate_cax_offset_images()

    if run_analysis_on_generated:
        status_callback("Analyzing generated images…")
        analyze_all(output_dir=output_gen_dir, status_callback=status_callback, output_format=results_as_json)


    # Example: respect other options
    if "Run analysis on generated images" in other_options:
        pass  # ← run analysis on generated images


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AnalysisGUI()
    app.mainloop()
