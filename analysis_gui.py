"""
analysis_gui.py

A reusable tkinter GUI for image generation and analysis options.
Customize the ANALYSIS_OPTIONS and DISPLAY_OPTIONS lists to match your needs,
then wire up the `run_analysis` function at the bottom to call your main logic.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading

# ── Customize your options here ──────────────────────────────────────────────

IMAGE_TYPE_OPTIONS = [
    "Flatness",
    "Field Size",
    "Symmetry",
    "Orthogonality",
    "CAX Offset",
]

DISPLAY_OPTIONS = [
    "Show preview after generation",
    "Overlay annotations",
    "Use dark background",
    "Save intermediate steps",
]

# ─────────────────────────────────────────────────────────────────────────────


class AnalysisGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DICOM Image Generator")
        self.resizable(False, False)
        self.configure(bg="#e0e0f0")

        self._build_styles()
        self._build_ui()

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
        ttk.Label(outer, text="DICOM Image Generator", style="Header.TLabel").pack(
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
            var = tk.BooleanVar(value=False)
            self.image_type_vars[opt] = var
            col = 0 if i < mid else 1
            row = i if i < mid else i - mid
            cb = ttk.Checkbutton(col_frame, text=opt, variable=var)
            cb.grid(row=row, column=col, sticky="w", padx=(0, 24), pady=2)

        # ── Display options ───────────────────────────────────────────────────
        display_card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        display_card.pack(fill="x", pady=(0, 10))

        ttk.Label(
            display_card, text="DISPLAY OPTIONS", style="Section.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        self.display_vars = {}
        for opt in DISPLAY_OPTIONS:
            var = tk.BooleanVar(value=False)
            self.display_vars[opt] = var
            ttk.Checkbutton(display_card, text=opt, variable=var).pack(
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

    def _on_run(self):
        """Validate inputs, then run analysis in a background thread."""
        if not self.folder_var.get():
            self._set_status("⚠  Please select an output directory first.", error=True)
            return

        chosen_image_type = [k for k, v in self.image_type_vars.items() if v.get()]
        chosen_display = [k for k, v in self.display_vars.items() if v.get()]

        self.run_btn.configure(state="disabled")
        self.progress.start(12)
        self._set_status("Running…")

        def worker():
            try:
                run_analysis(
                    output_dir=self.folder_var.get(),
                    image_type_options=chosen_image_type,
                    display_options=chosen_display,
                    status_callback=self._set_status,
                )
                self.after(0, lambda: self._set_status("✔  Done!"))
            except Exception as exc:
                self.after(0, lambda: self._set_status(f"✖  Error: {exc}", error=True))
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

def run_analysis(output_dir, image_type_options, display_options, status_callback):
    """
    Replace the body of this function with your image generation / analysis logic.

    Args:
        output_dir      (str):       Folder path chosen by the user.
        image_type_options (list[str]): Names of checked image type options.
        display_options  (list[str]): Names of checked display options.
        status_callback  (callable):  Call status_callback("message") to update
                                      the status bar from your worker thread.
    """
    import time  # remove once you add real logic

    status_callback("Generating images…")
    time.sleep(1.5)  # ← replace with your image generation code

    for opt in image_type_options:
        status_callback(f"Running {opt}…")
        time.sleep(0.8)  # ← replace with actual analysis per option

    # Example: respect display options
    if "Show preview after generation" in display_options:
        pass  # ← open your preview window here


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = AnalysisGUI()
    app.mainloop()
