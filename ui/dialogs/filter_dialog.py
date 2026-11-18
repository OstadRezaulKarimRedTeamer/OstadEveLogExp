"""
Event Log Explorer - Advanced Filter Dialog
Allows building multi-condition filter queries matching Event Log Explorer.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from datetime import datetime
from backend.models import FilterCriteria
from backend.filter_engine import parse_id_ranges


class FilterDialog(tk.Toplevel):
    """Filter dialog with comprehensive criteria selection."""

    def __init__(
        self,
        parent: tk.Widget,
        current_criteria: FilterCriteria,
        available_sources: List[str],
        on_apply: Callable[[FilterCriteria], None]
    ):
        super().__init__(parent)
        self.title("Filter Log Events - Event Log Explorer")
        self.geometry("560x620")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.criteria = current_criteria
        self.available_sources = sorted(available_sources)
        self.on_apply = on_apply

        self._build_ui()
        self._load_criteria()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Event Levels Frame
        lvl_frame = ttk.LabelFrame(main_frame, text="Event Levels", padding=8)
        lvl_frame.pack(fill=tk.X, pady=(0, 8))

        self.lvl_vars = {}
        levels = ["Critical", "Error", "Warning", "Information", "Audit Success", "Audit Failure", "Verbose"]
        
        row, col = 0, 0
        for lvl in levels:
            var = tk.BooleanVar(value=lvl in self.criteria.levels)
            cb = ttk.Checkbutton(lvl_frame, text=lvl, variable=var)
            cb.grid(row=row, column=col, sticky=tk.W, padx=8, pady=3)
            self.lvl_vars[lvl] = var
            col += 1
            if col > 3:
                col = 0
                row += 1

        # 2. Event IDs Frame
        id_frame = ttk.LabelFrame(main_frame, text="Event IDs", padding=8)
        id_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(id_frame, text="Include IDs (e.g. 4624, 4625, 7000-7050):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_ids_include = ttk.Entry(id_frame, width=55)
        self.entry_ids_include.grid(row=1, column=0, sticky=tk.W, pady=(0, 4))

        ttk.Label(id_frame, text="Exclude IDs:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_ids_exclude = ttk.Entry(id_frame, width=55)
        self.entry_ids_exclude.grid(row=3, column=0, sticky=tk.W, pady=(0, 2))

        # 3. Sources Frame
        src_frame = ttk.LabelFrame(main_frame, text="Event Sources / Providers", padding=8)
        src_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(src_frame, text="Source contains (comma separated):").pack(anchor=tk.W, pady=(0, 2))
        self.entry_sources = ttk.Entry(src_frame)
        self.entry_sources.pack(fill=tk.X, pady=(0, 4))

        # 4. User Accounts Frame
        user_frame = ttk.LabelFrame(main_frame, text="User Accounts", padding=8)
        user_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(user_frame, text="User name contains (comma separated, e.g. SYSTEM, Administrator):").pack(anchor=tk.W, pady=(0, 2))
        self.entry_users = ttk.Entry(user_frame)
        self.entry_users.pack(fill=tk.X, pady=(0, 4))

        # 5. Search Text Frame
        search_frame = ttk.LabelFrame(main_frame, text="Full-text Description Filter", padding=8)
        search_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_frame, text="Description contains:").pack(anchor=tk.W, pady=(0, 2))
        self.entry_search = ttk.Entry(search_frame)
        self.entry_search.pack(fill=tk.X, pady=(0, 4))

        # Bottom Buttons
        btn_box = ttk.Frame(main_frame)
        btn_box.pack(fill=tk.X, pady=(8, 0))

        btn_reset = ttk.Button(btn_box, text="🔄 Reset All", command=self._reset_fields)
        btn_reset.pack(side=tk.LEFT)

        btn_cancel = ttk.Button(btn_box, text="Cancel", command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT, padx=(6, 0))

        btn_apply = ttk.Button(btn_box, text="✔ Apply Filter", command=self._apply_filter)
        btn_apply.pack(side=tk.RIGHT)

    def _load_criteria(self) -> None:
        if self.criteria.event_ids_include:
            self.entry_ids_include.insert(0, ", ".join(str(i) for i in sorted(self.criteria.event_ids_include)))
        if self.criteria.event_ids_exclude:
            self.entry_ids_exclude.insert(0, ", ".join(str(i) for i in sorted(self.criteria.event_ids_exclude)))
        if self.criteria.sources_include:
            self.entry_sources.insert(0, ", ".join(self.criteria.sources_include))
        if self.criteria.users_include:
            self.entry_users.insert(0, ", ".join(self.criteria.users_include))
        if self.criteria.search_text:
            self.entry_search.insert(0, self.criteria.search_text)

    def _reset_fields(self) -> None:
        for var in self.lvl_vars.values():
            var.set(True)
        self.entry_ids_include.delete(0, tk.END)
        self.entry_ids_exclude.delete(0, tk.END)
        self.entry_sources.delete(0, tk.END)
        self.entry_users.delete(0, tk.END)
        self.entry_search.delete(0, tk.END)

    def _apply_filter(self) -> None:
        selected_levels = [lvl for lvl, var in self.lvl_vars.items() if var.get()]
        if not selected_levels:
            messagebox.showwarning("Filter Warning", "Please select at least one event level.", parent=self)
            return

        inc_ids = list(parse_id_ranges(self.entry_ids_include.get()))
        exc_ids = list(parse_id_ranges(self.entry_ids_exclude.get()))
        
        src_raw = self.entry_sources.get().strip()
        sources = [s.strip() for s in src_raw.split(",") if s.strip()] if src_raw else []

        user_raw = self.entry_users.get().strip()
        users = [u.strip() for u in user_raw.split(",") if u.strip()] if user_raw else []

        search_txt = self.entry_search.get().strip()

        new_crit = FilterCriteria(
            levels=selected_levels,
            event_ids_include=inc_ids,
            event_ids_exclude=exc_ids,
            sources_include=sources,
            users_include=users,
            search_text=search_txt,
            date_from=self.criteria.date_from,
            date_to=self.criteria.date_to
        )

        self.on_apply(new_crit)
        self.destroy()
