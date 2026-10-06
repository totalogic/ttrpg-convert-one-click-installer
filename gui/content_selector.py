"""Content Selector GUI for ttrpg-convert-cli.

Provides a graphical interface for:
- Selecting content sources (books, adventures, reference, homebrew)
- Choosing between local directory or git repository output
- Generating a ttrpg-convert-cli configuration file
- Running the conversion
"""

from __future__ import annotations

import json
import os
import queue
import shlex
import signal
import subprocess
import sys
import threading
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path


import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .source_map import (
    OPEN_REFERENCE,
    SOURCES_5E_ADVENTURES,
    SOURCES_5E_BOOKS,
    SOURCES_5E_REFERENCE,
    SOURCES_PF2E_BOOKS,
    REPRINT_BEHAVIORS,
    DEFAULT_CONFIG,
    all_5e_sources,
    source_name_map,
)

UPSTREAM_URL = "https://github.com/ebullient/ttrpg-convert-cli"
PROJECT_URL = "https://github.com/totalogic/ttrpg-convert-one-click-installer"


@dataclass
class ContentSelection:
    """User's content selections for the conversion config."""

    # Source selections: each maps source-id -> include as "full" or "reference"
    books: dict[str, bool] = field(default_factory=dict)
    adventures: dict[str, bool] = field(default_factory=dict)
    reference: dict[str, bool] = field(default_factory=dict)
    homebrew_files: list[str] = field(default_factory=list)

    # Output settings
    output_location: str = "local"  # "local" or "remote"
    local_path: str = ""
    remote_repo_url: str = ""
    remote_branch: str = "main"
    remote_subdir: str = ""

    # Conversion options
    reprint_behavior: str = "newest"
    races_as_species: bool = True
    split_rules: bool = True
    use_dice_roller: bool = False
    tag_prefix: str = "ttrpg-cli"
    copy_internal_images: bool = False
    copy_external_images: bool = False
    images_root: str = ""

    # 5etools data source
    data_dir: str = ""  # existing 5etools data directory
    use_downloaded_data: bool = True  # download from 5etools-mirror if no data_dir


class ContentSelectorApp:
    """Main content selector application."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.selection = ContentSelection()
        self.process: subprocess.Popen[str] | None = None
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.operation_active = False
        self.cancel_requested = threading.Event()
        self.completed_output = ""

        # Initialize selection dicts
        for sid, _ in SOURCES_5E_BOOKS:
            self.selection.books[sid] = False
        for sid, _ in SOURCES_5E_ADVENTURES:
            self.selection.adventures[sid] = False
        for sid, _ in SOURCES_5E_REFERENCE:
            self.selection.reference[sid] = False
        # Open reference sources selected by default
        for sid, _ in OPEN_REFERENCE:
            self.selection.reference[sid] = True

        self._configure_window()
        self._build_ui()
        self.root.after(100, self._process_events)

    def _configure_window(self) -> None:
        self.root.title("TTRPG Convert — Content Selector")
        self.root.geometry("900x780")
        self.root.minsize(750, 680)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        style = ttk.Style(self.root)
        available = style.theme_names()
        if "vista" in available:
            style.theme_use("vista")
        elif "clam" in available:
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)

        # Notebook for tabbed content selection
        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)

        # --- Tab: 5e Books ---
        self.books_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.books_tab, text="Books (5e)")
        self._build_source_grid(self.books_tab, SOURCES_5E_BOOKS, "books")

        # --- Tab: Adventures ---
        self.adventures_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.adventures_tab, text="Adventures (5e)")
        self._build_source_grid(self.adventures_tab, SOURCES_5E_ADVENTURES, "adventures")

        # --- Tab: Reference ---
        self.reference_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.reference_tab, text="Reference (5e)")
        ref_all = SOURCES_5E_REFERENCE + OPEN_REFERENCE
        self._build_source_grid(self.reference_tab, ref_all, "reference")

        # --- Tab: Homebrew ---
        self.homebrew_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.homebrew_tab, text="Homebrew")
        self._build_homebrew_tab(self.homebrew_tab)

        # --- Tab: Output & Options ---
        self.options_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.options_tab, text="Output & Options")
        self._build_options_tab(self.options_tab)

        # --- Tab: Preview & Run ---
        self.preview_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.preview_tab, text="Preview & Run")
        self._build_preview_tab(self.preview_tab)

    def _build_source_grid(
        self,
        parent: ttk.Frame,
        sources: list[tuple[str, str]],
        category: str,
    ) -> None:
        """Build a scrollable grid of checkboxes for source selection."""
        # Search bar
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(search_frame, text="Filter:").pack(side="left")
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Scrollable canvas
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Build checkboxes
        checkboxes: list[tuple[ttk.Checkbutton, tk.BooleanVar, str]] = []
        for idx, (sid, name) in enumerate(sources):
            row = idx // 3
            col = idx % 3
            var = tk.BooleanVar(
                value=getattr(self.selection, category).get(sid, False)
            )
            cb = ttk.Checkbutton(
                scroll_frame,
                text=f"{sid} — {name}",
                variable=var,
                command=lambda s=sid, v=var, cat=category: self._on_toggle(s, v, cat),
            )
            cb.grid(row=row, column=col, sticky="w", padx=(0, 12), pady=2)
            checkboxes.append((cb, var, sid))

        # Select all / deselect all
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=(4, 0))
        ttk.Button(
            btn_frame,
            text="Select all",
            command=lambda: self._toggle_all(checkboxes, True),
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            btn_frame,
            text="Deselect all",
            command=lambda: self._toggle_all(checkboxes, False),
        ).pack(side="left")

        # Filter functionality
        def filter_sources(_event=None):
            query = search_var.get().lower()
            for cb, var, sid in checkboxes:
                text = cb.cget("text").lower()
                cb.grid()  # ensure visible
                if query and query not in text:
                    cb.grid_remove()
                else:
                    cb.grid()

        search_entry.bind("<KeyRelease>", filter_sources)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    def _toggle_all(
        self,
        checkboxes: list[tuple[ttk.Checkbutton, tk.BooleanVar, str]],
        state: bool,
    ) -> None:
        for cb, var, sid in checkboxes:
            var.set(state)

    def _on_toggle(self, sid: str, var: tk.BooleanVar, category: str) -> None:
        target: dict[str, bool] = getattr(self.selection, category)
        target[sid] = var.get()

    def _build_homebrew_tab(self, parent: ttk.Frame) -> None:
        ttk.Label(
            parent,
            text="Add homebrew JSON files to include in the conversion.\n"
            "Each file should be a complete homebrew reference (not 5etools data).",
            style="Subtitle.TLabel",
            wraplength=600,
        ).pack(anchor="w", pady=(0, 10))

        # Homebrew file list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="both", expand=True)

        self.hb_listbox = tk.Listbox(list_frame, height=10)
        self.hb_listbox.pack(side="left", fill="both", expand=True)
        hb_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.hb_listbox.yview
        )
        hb_scroll.pack(side="right", fill="y")
        self.hb_listbox.configure(yscrollcommand=hb_scroll.set)

        # Buttons
        hb_btn_frame = ttk.Frame(parent)
        hb_btn_frame.pack(fill="x", pady=(8, 0))
        ttk.Button(hb_btn_frame, text="Add file…", command=self._add_homebrew).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(
            hb_btn_frame, text="Remove selected", command=self._remove_homebrew
        ).pack(side="left")
        ttk.Button(hb_btn_frame, text="Clear all", command=self._clear_homebrew).pack(
            side="left", padx=(6, 0)
        )

    def _add_homebrew(self) -> None:
        files = filedialog.askopenfilenames(
            title="Select homebrew JSON files",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        for f in files:
            if f not in self.selection.homebrew_files:
                self.selection.homebrew_files.append(f)
                self.hb_listbox.insert("end", f)

    def _remove_homebrew(self) -> None:
        selected = self.hb_listbox.curselection()
        if not selected:
            return
        for idx in reversed(selected):
            path = self.hb_listbox.get(idx)
            if path in self.selection.homebrew_files:
                self.selection.homebrew_files.remove(path)
            self.hb_listbox.delete(idx)

    def _clear_homebrew(self) -> None:
        self.selection.homebrew_files.clear()
        self.hb_listbox.delete(0, "end")

    def _build_options_tab(self, parent: ttk.Frame) -> None:
        # --- Output location ---
        loc_frame = ttk.LabelFrame(
            parent, text="Save Location", style="Section.TLabelframe", padding=10
        )
        loc_frame.pack(fill="x", pady=(0, 10))
        loc_frame.columnconfigure(1, weight=1)

        self.output_location_var = tk.StringVar(value="local")
        ttk.Radiobutton(
            loc_frame,
            text="Local directory",
            variable=self.output_location_var,
            value="local",
            command=self._sync_location,
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(loc_frame, text="Output path").grid(row=1, column=0, sticky="w")
        self.local_path_var = tk.StringVar(
            value=str(Path.home() / "Documents" / "TTRPG-Content")
        )
        ttk.Entry(loc_frame, textvariable=self.local_path_var).grid(
            row=1, column=1, sticky="ew", padx=8
        )
        ttk.Button(
            loc_frame, text="Browse…", command=self._choose_local_path
        ).grid(row=1, column=2)

        ttk.Radiobutton(
            loc_frame,
            text="Remote repository (git)",
            variable=self.output_location_var,
            value="remote",
            command=self._sync_location,
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))

        ttk.Label(loc_frame, text="Repository URL").grid(row=3, column=0, sticky="w")
        self.remote_repo_var = tk.StringVar()
        ttk.Entry(
            loc_frame,
            textvariable=self.remote_repo_var,
            width=50,
        ).grid(row=3, column=1, sticky="ew", padx=8)
        ttk.Label(loc_frame, text="e.g. https://github.com/user/my-vault").grid(
            row=4, column=1, sticky="w", padx=8
        )

        ttk.Label(loc_frame, text="Branch").grid(row=5, column=0, sticky="w", pady=(4, 0))
        self.remote_branch_var = tk.StringVar(value="main")
        ttk.Entry(
            loc_frame, textvariable=self.remote_branch_var, width=20
        ).grid(row=5, column=1, sticky="w", padx=8, pady=(4, 0))

        ttk.Label(loc_frame, text="Subdirectory (optional)").grid(
            row=6, column=0, sticky="w", pady=(4, 0)
        )
        self.remote_subdir_var = tk.StringVar()
        ttk.Entry(loc_frame, textvariable=self.remote_subdir_var).grid(
            row=6, column=1, sticky="w", padx=8, pady=(4, 0)
        )

        # --- Data source ---
        data_frame = ttk.LabelFrame(
            parent,
            text="5etools Data Source",
            style="Section.TLabelframe",
            padding=10,
        )
        data_frame.pack(fill="x", pady=(0, 10))
        data_frame.columnconfigure(1, weight=1)

        self.use_downloaded_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(
            data_frame,
            text="Download from 5etools-mirror-3 automatically",
            variable=self.use_downloaded_var,
            value=True,
            command=self._sync_data_source,
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Radiobutton(
            data_frame,
            text="Use an existing local 5etools data directory",
            variable=self.use_downloaded_var,
            value=False,
            command=self._sync_data_source,
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        ttk.Label(data_frame, text="Data directory").grid(row=2, column=0, sticky="w")
        self.data_dir_var = tk.StringVar()
        self.data_dir_entry = ttk.Entry(data_frame, textvariable=self.data_dir_var)
        self.data_dir_entry.grid(row=2, column=1, sticky="ew", padx=8)
        self.data_dir_btn = ttk.Button(
            data_frame, text="Browse…", command=self._choose_data_dir
        )
        self.data_dir_btn.grid(row=2, column=2)
        self._sync_data_source()

        # --- Conversion options ---
        conv_frame = ttk.LabelFrame(
            parent,
            text="Conversion Options",
            style="Section.TLabelframe",
            padding=10,
        )
        conv_frame.pack(fill="x", pady=(0, 10))
        conv_frame.columnconfigure(1, weight=1)

        ttk.Label(conv_frame, text="Reprint behavior").grid(
            row=0, column=0, sticky="w"
        )
        self.reprint_var = tk.StringVar(value="newest")
        reprint_combo = ttk.Combobox(
            conv_frame,
            textvariable=self.reprint_var,
            values=REPRINT_BEHAVIORS,
            state="readonly",
            width=12,
        )
        reprint_combo.grid(row=0, column=1, sticky="w", padx=8)

        self.races_as_species_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            conv_frame,
            text="Render races as species",
            variable=self.races_as_species_var,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.split_rules_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            conv_frame,
            text="Split rules into separate files",
            variable=self.split_rules_var,
        ).grid(row=2, column=0, columnspan=2, sticky="w")

        self.use_dice_roller_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            conv_frame,
            text="Use Obsidian dice roller plugin",
            variable=self.use_dice_roller_var,
        ).grid(row=3, column=0, columnspan=2, sticky="w")

        ttk.Label(conv_frame, text="Tag prefix").grid(row=4, column=0, sticky="w", pady=(6, 0))
        self.tag_prefix_var = tk.StringVar(value="ttrpg-cli")
        ttk.Entry(conv_frame, textvariable=self.tag_prefix_var, width=20).grid(
            row=4, column=1, sticky="w", padx=8, pady=(6, 0)
        )

        # --- Images ---
        img_frame = ttk.LabelFrame(
            parent, text="Images", style="Section.TLabelframe", padding=10
        )
        img_frame.pack(fill="x")

        self.copy_internal_images_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            img_frame,
            text="Copy internal images into vault",
            variable=self.copy_internal_images_var,
        ).grid(row=0, column=0, sticky="w")

        self.copy_external_images_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            img_frame,
            text="Download and copy external images into vault",
            variable=self.copy_external_images_var,
        ).grid(row=1, column=0, sticky="w")

        ttk.Label(img_frame, text="Internal image root (optional)").grid(
            row=2, column=0, sticky="w", pady=(4, 0)
        )
        self.images_root_var = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.images_root_var).grid(
            row=3, column=0, sticky="ew", pady=(2, 0)
        )

    def _build_preview_tab(self, parent: ttk.Frame) -> None:
        # Config preview
        ttk.Label(
            parent,
            text="Generated configuration preview:",
            style="Section.TLabelframe.Label",
        ).pack(anchor="w")

        self.config_preview = scrolledtext.ScrolledText(
            parent,
            height=12,
            wrap="word",
            font=("Consolas", 9),
            state="disabled",
        )
        self.config_preview.pack(fill="x", pady=(4, 10))

        # Command preview
        ttk.Label(
            parent,
            text="Conversion command:",
            style="Section.TLabelframe.Label",
        ).pack(anchor="w")

        self.command_preview = scrolledtext.ScrolledText(
            parent,
            height=3,
            wrap="word",
            font=("Consolas", 9),
            state="disabled",
        )
        self.command_preview.pack(fill="x", pady=(4, 10))

        # Action buttons
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x")
        ttk.Button(
            action_frame,
            text="Refresh preview",
            command=self._refresh_preview,
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            action_frame,
            text="Save config file…",
            command=self._save_config_file,
        ).pack(side="left", padx=(0, 8))
        self.run_button = ttk.Button(
            action_frame,
            text="Run conversion",
            style="Primary.TButton",
            command=self._run_conversion,
        )
        self.run_button.pack(side="left", padx=(0, 8))
        self.cancel_button = ttk.Button(
            action_frame,
            text="Cancel",
            command=self._cancel,
            state="disabled",
        )
        self.cancel_button.pack(side="left", padx=(0, 8))

        # Progress log
        log_frame = ttk.LabelFrame(
            parent,
            text="Progress",
            style="Section.TLabelframe",
            padding=8,
        )
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.progress = ttk.Progressbar(log_frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))
        self.log = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap="word",
            state="disabled",
            font=("Consolas", 9),
        )
        self.log.pack(fill="both", expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(action_frame, textvariable=self.status_var).pack(
            side="right"
        )

    def _sync_location(self) -> None:
        self.selection.output_location = self.output_location_var.get()

    def _sync_data_source(self) -> None:
        use_downloaded = self.use_downloaded_var.get()
        state = "disabled" if use_downloaded else "normal"
        self.data_dir_entry.configure(state=state)
        self.data_dir_btn.configure(state=state)

    def _choose_local_path(self) -> None:
        selected = filedialog.askdirectory(
            title="Choose output directory",
            initialdir=str(Path.home() / "Documents"),
        )
        if selected:
            self.local_path_var.set(selected)

    def _choose_data_dir(self) -> None:
        selected = filedialog.askdirectory(
            title="Choose a 5etools directory containing a data folder",
            initialdir=str(Path.home()),
        )
        if selected:
            self.data_dir_var.set(selected)

    def _refresh_preview(self) -> None:
        """Update the config and command preview text areas."""
        self._sync_selection()
        config = self._generate_config()
        cmd = self._build_command(config)

        self.config_preview.configure(state="normal")
        self.config_preview.delete("1.0", "end")
        self.config_preview.insert("1.0", json.dumps(config, indent=2))
        self.config_preview.configure(state="disabled")

        self.command_preview.configure(state="normal")
        self.command_preview.delete("1.0", "end")
        cmd_str = " ".join(shlex.quote(c) for c in cmd) if cmd else "—"
        self.command_preview.insert("1.0", cmd_str)
        self.command_preview.configure(state="disabled")

    def _sync_selection(self) -> None:
        """Sync all tk variables into the ContentSelection dataclass."""
        self.selection.output_location = self.output_location_var.get()
        self.selection.local_path = self.local_path_var.get().strip()
        self.selection.remote_repo_url = self.remote_repo_var.get().strip()
        self.selection.remote_branch = self.remote_branch_var.get().strip() or "main"
        self.selection.remote_subdir = self.remote_subdir_var.get().strip()
        self.selection.data_dir = self.data_dir_var.get().strip()
        self.selection.use_downloaded_data = self.use_downloaded_var.get()
        self.selection.reprint_behavior = self.reprint_var.get()
        self.selection.races_as_species = self.races_as_species_var.get()
        self.selection.split_rules = self.split_rules_var.get()
        self.selection.use_dice_roller = self.use_dice_roller_var.get()
        self.selection.tag_prefix = self.tag_prefix_var.get().strip() or "ttrpg-cli"
        self.selection.copy_internal_images = self.copy_internal_images_var.get()
        self.selection.copy_external_images = self.copy_external_images_var.get()
        self.selection.images_root = self.images_root_var.get().strip()

    def _generate_config(self) -> dict:
        """Build a ttrpg-convert-cli compatible config dict."""
        sources: dict[str, list[str]] = {}

        selected_books = [sid for sid, val in self.selection.books.items() if val]
        selected_adventures = [
            sid for sid, val in self.selection.adventures.items() if val
        ]
        selected_reference = [
            sid for sid, val in self.selection.reference.items() if val
        ]

        if selected_books:
            sources["book"] = selected_books
        if selected_adventures:
            sources["adventure"] = selected_adventures
        if selected_reference:
            sources["reference"] = selected_reference
        if self.selection.homebrew_files:
            sources["homebrew"] = list(self.selection.homebrew_files)

        config: dict = {"sources": sources}
        config["reprintBehavior"] = self.selection.reprint_behavior
        config["racesAsSpecies"] = self.selection.races_as_species
        config["splitRules"] = self.selection.split_rules
        if self.selection.use_dice_roller:
            config["useDiceRoller"] = True
        config["tagPrefix"] = self.selection.tag_prefix
        config["images"] = {
            "copyInternal": self.selection.copy_internal_images,
            "copyExternal": self.selection.copy_external_images,
        }
        if self.selection.images_root:
            config["images"]["internalRoot"] = self.selection.images_root

        return config

    def _resolve_output_dir(self) -> Path:
        """Determine the output directory based on selection."""
        if self.selection.output_location == "local":
            return Path(self.selection.local_path).expanduser().resolve()
        else:
            # For remote, we clone into a temp dir then push
            repo_url = self.selection.remote_repo_url
            if not repo_url:
                raise ValueError("No repository URL specified")
            # Use a temp directory for the clone
            import tempfile

            base = Path(tempfile.gettempdir()) / "ttrpg-convert-remote"
            return base / "output"

    def _build_command(self, config: dict | None = None) -> list[str]:
        """Build the ttrpg-convert command."""
        if config is None:
            config = self._generate_config()

        # Find ttrpg-convert executable
        if sys.platform == "win32":
            bin_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ttrpg-convert-cli" / "bin" / "ttrpg-convert.exe"
        else:
            bin_path = Path.home() / ".local" / "bin" / "ttrpg-convert"

        convert_cmd = str(bin_path)
        output_dir = str(self._resolve_output_dir())

        # Config file path
        import tempfile

        config_path = Path(tempfile.gettempdir()) / "ttrpg-content-selector-config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        cmd = [
            convert_cmd,
            "--index",
            "-c",
            str(config_path),
            "-o",
            output_dir,
        ]

        # Data source
        if self.selection.use_downloaded_data or not self.selection.data_dir:
            # Will need the 5etools data dir; the installer handles this
            data_dir = str(
                Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "ttrpg-convert-data"
            )
            cmd.append(data_dir)
        else:
            cmd.append(self.selection.data_dir)

        return cmd

    def _save_config_file(self) -> None:
        self._sync_selection()
        config = self._generate_config()
        path = filedialog.asksaveasfilename(
            title="Save configuration file",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo(
                "Saved",
                f"Configuration saved to:\n{path}",
                parent=self.root,
            )
        except OSError as exc:
            messagebox.showerror(
                "Save failed",
                f"Could not save file: {exc}",
                parent=self.root,
            )

    def _run_conversion(self) -> None:
        if self.operation_active:
            return

        self._sync_selection()

        # Validate
        if self.selection.output_location == "local":
            if not self.selection.local_path:
                messagebox.showerror(
                    "Missing output path",
                    "Please specify a local output directory.",
                    parent=self.root,
                )
                return
        else:
            if not self.selection.remote_repo_url:
                messagebox.showerror(
                    "Missing repository URL",
                    "Please specify a git repository URL.",
                    parent=self.root,
                )
                return

        # Check if any sources are selected
        total_selected = (
            sum(self.selection.books.values())
            + sum(self.selection.adventures.values())
            + sum(self.selection.reference.values())
            + len(self.selection.homebrew_files)
        )
        if total_selected == 0:
            messagebox.showerror(
                "No content selected",
                "Please select at least one content source to convert.",
                parent=self.root,
            )
            return

        config = self._generate_config()
        cmd = self._build_command(config)

        # For remote: clone repo first
        if self.selection.output_location == "remote":
            self._run_remote_conversion(cmd, config)
            return

        # Local conversion
        output_dir = Path(self.selection.local_path).expanduser().resolve()
        if output_dir.exists() and not output_dir.is_dir():
            messagebox.showerror(
                "Invalid output",
                "The output path exists but is not a directory.",
                parent=self.root,
            )
            return
        output_dir.mkdir(parents=True, exist_ok=True)

        self._append_log(f"$ {' '.join(shlex.quote(c) for c in cmd)}\n")
        self.status_var.set("Converting…")
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.start(12)
        self.operation_active = True
        self.cancel_requested.clear()

        thread = threading.Thread(
            target=self._run_process, args=(cmd,), daemon=True
        )
        thread.start()

    def _run_remote_conversion(self, cmd: list[str], config: dict) -> None:
        """For remote repo: clone, convert into clone, commit, and push."""
        import tempfile

        repo_url = self.selection.remote_repo_url
        branch = self.selection.remote_branch
        subdir = self.selection.remote_subdir

        try:
            tmp_dir = Path(tempfile.mkdtemp(prefix="ttrpg-remote-"))
            clone_cmd = ["git", "clone", "--branch", branch, repo_url, str(tmp_dir)]

            self._append_log(f"$ {' '.join(shlex.quote(c) for c in clone_cmd)}\n")
            self.status_var.set("Cloning repository…")
            self.run_button.configure(state="disabled")
            self.cancel_button.configure(state="normal")
            self.progress.start(12)
            self.operation_active = True
            self.cancel_requested.clear()

            # Modify cmd to output into the cloned repo subdir
            output_path = tmp_dir / subdir if subdir else tmp_dir
            output_path.mkdir(parents=True, exist_ok=True)

            # Rebuild command with correct output path
            for i, c in enumerate(cmd):
                if c == "-o":
                    cmd[i + 1] = str(output_path)
                    break

            full_sequence = [
                ("clone", clone_cmd),
                ("convert", cmd),
                (
                    "commit",
                    [
                        "git",
                        "-C",
                        str(tmp_dir),
                        "add",
                        "-A",
                    ],
                ),
                (
                    "commit2",
                    [
                        "git",
                        "-C",
                        str(tmp_dir),
                        "commit",
                        "-m",
                        "TTRPG Convert: generated content",
                    ],
                ),
                (
                    "push",
                    ["git", "-C", str(tmp_dir), "push", "origin", branch],
                ),
            ]

            self.remote_tmp_dir = tmp_dir

            thread = threading.Thread(
                target=self._run_remote_process,
                args=(full_sequence,),
                daemon=True,
            )
            thread.start()

        except Exception as exc:
            self._fail(exc)

    def _run_process(self, cmd: list[str]) -> None:
        try:
            if self.cancel_requested.is_set():
                self.events.put(("cancelled", None))
                return
            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=creationflags,
                start_new_session=sys.platform != "win32",
            )
            self.process = process
            if self.cancel_requested.is_set():
                self._terminate(process)
            assert process.stdout is not None
            for line in process.stdout:
                self.events.put(("log", line))
            return_code = process.wait()
            if self.cancel_requested.is_set():
                self.events.put(("cancelled", None))
            else:
                self.events.put(("done", return_code))
        except Exception as exc:
            self.events.put(("error", exc))
        finally:
            self.process = None

    def _run_remote_process(
        self,
        sequence: list[tuple[str, list[str]]],
    ) -> None:
        try:
            for label, cmd in sequence:
                if self.cancel_requested.is_set():
                    self.events.put(("cancelled", None))
                    return
                self.events.put(("log", f"\n==> {label}\n"))
                startupinfo = None
                creationflags = 0
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                    startupinfo=startupinfo,
                    creationflags=creationflags,
                    start_new_session=sys.platform != "win32",
                )
                self.process = process
                assert process.stdout is not None
                for line in process.stdout:
                    self.events.put(("log", line))
                rc = process.wait()
                if rc != 0:
                    self.events.put(("error", f"{label} failed with exit code {rc}"))
                    return
            self.events.put(("done", 0))
        except Exception as exc:
            self.events.put(("error", exc))
        finally:
            self.process = None

    def _process_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "log":
                    self._append_log(str(payload))
                elif event == "done":
                    self._finish(int(payload))  # type: ignore[arg-type]
                elif event == "error":
                    self._fail(payload)
                elif event == "cancelled":
                    self._cancelled()
        except queue.Empty:
            pass
        self.root.after(100, self._process_events)

    def _finish(self, return_code: int) -> None:
        self.operation_active = False
        self.progress.stop()
        self.run_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        if return_code == 0:
            self.status_var.set("Conversion complete")
            self._append_log("\nConversion complete.\n")
            messagebox.showinfo(
                "Complete",
                "Content conversion completed successfully.",
                parent=self.root,
            )
        else:
            self.status_var.set(f"Failed (exit code {return_code})")
            self._append_log(f"\nConversion failed with exit code {return_code}.\n")
            messagebox.showerror(
                "Conversion failed",
                f"The converter exited with code {return_code}.\n"
                "Review the progress log for details.",
                parent=self.root,
            )

    def _fail(self, error: object) -> None:
        self.operation_active = False
        self.progress.stop()
        self.run_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.status_var.set("Failed")
        self._append_log(f"ERROR: {error}\n")
        messagebox.showerror("Error", str(error), parent=self.root)

    def _cancelled(self) -> None:
        self.operation_active = False
        self.progress.stop()
        self.run_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.status_var.set("Cancelled")
        self._append_log("Operation cancelled.\n")

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _cancel(self) -> None:
        if not self.operation_active:
            return
        self.status_var.set("Cancelling…")
        self.cancel_button.configure(state="disabled")
        self.cancel_requested.set()
        proc = self.process
        if proc is not None:
            threading.Thread(
                target=self._terminate, args=(proc,), daemon=True
            ).start()

    def _terminate(self, process: subprocess.Popen[str]) -> None:
        if process.poll() is not None:
            return
        if sys.platform == "win32":
            try:
                subprocess.run(
                    ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=5,
                    check=False,
                )
                process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                if process.poll() is None:
                    process.kill()
        else:
            try:
                pgid = os.getpgid(process.pid)
                os.killpg(pgid, signal.SIGTERM)
                process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    pgid = os.getpgid(process.pid)
                    os.killpg(pgid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def _on_close(self) -> None:
        if self.operation_active:
            if not messagebox.askyesno(
                "Operation in progress",
                "Stop the current operation and close?",
                parent=self.root,
            ):
                return
            self._cancel()
            self.root.after(2000, self.root.destroy)
            return
        self.root.destroy()


def main() -> int:
    root = tk.Tk()
    ContentSelectorApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
