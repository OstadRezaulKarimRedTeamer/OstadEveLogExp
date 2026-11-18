"""
Event Log Explorer - Create Task from Template Wizard
Matches the exact dialog shown in Screenshot 2.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from backend.models import TaskTemplate
from backend.templates import TASK_TEMPLATES


class CreateTaskFromTemplateDialog(tk.Toplevel):
    """Create task from template wizard matching Screenshot 2."""

    def __init__(
        self,
        parent: tk.Widget,
        template: TaskTemplate,
        on_finish: Callable[[TaskTemplate, str], None]
    ):
        super().__init__(parent)
        self.title("Create task from template")
        self.geometry("680x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.template = template
        self.on_finish = on_finish

        self._build_ui()
        self._load_template_data()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=8)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tabs: General, Log files, Filter, Columns, Start
        self.nb = ttk.Notebook(main_frame)
        self.nb.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.tab_general = ttk.Frame(self.nb, padding=10)
        self.tab_logfiles = ttk.Frame(self.nb, padding=10)
        self.tab_filter = ttk.Frame(self.nb, padding=10)
        self.tab_columns = ttk.Frame(self.nb, padding=10)
        self.tab_start = ttk.Frame(self.nb, padding=10)

        self.nb.add(self.tab_general, text=" General ")
        self.nb.add(self.tab_logfiles, text=" Log files ")
        self.nb.add(self.tab_filter, text=" Filter ")
        self.nb.add(self.tab_columns, text=" Columns ")
        self.nb.add(self.tab_start, text=" Start ")

        self._build_general_tab()
        self._build_filter_tab()
        self._build_logfiles_tab()

        # Select Filter tab by default (as seen in screenshot!)
        self.nb.select(self.tab_filter)

        # Bottom Action Bar
        bottom_bar = ttk.Frame(main_frame)
        bottom_bar.pack(fill=tk.X, pady=(4, 0))

        ttk.Button(bottom_bar, text="Load ▼", width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(bottom_bar, text="Save ▼", width=8).pack(side=tk.LEFT, padx=2)

        ttk.Button(bottom_bar, text="Cancel", width=9, command=self.destroy).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bottom_bar, text="Finish", width=9, command=self._do_finish).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bottom_bar, text="Next >", width=9, command=lambda: self._shift_tab(1)).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bottom_bar, text="< Back", width=9, command=lambda: self._shift_tab(-1)).pack(side=tk.RIGHT, padx=2)

    def _build_general_tab(self) -> None:
        ttk.Label(self.tab_general, text="Task Name:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.entry_task_name = ttk.Entry(self.tab_general, width=50)
        self.entry_task_name.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.tab_general, text="Description:").pack(anchor=tk.W, pady=(0, 2))
        self.txt_template_desc = tk.Text(self.tab_general, height=6, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_template_desc.pack(fill=tk.X, pady=(0, 10))

    def _build_logfiles_tab(self) -> None:
        ttk.Label(self.tab_logfiles, text="Target Channel / Sources:").pack(anchor=tk.W, pady=(0, 4))
        self.entry_channel = ttk.Entry(self.tab_logfiles, width=40)
        self.entry_channel.insert(0, self.template.target_channel)
        self.entry_channel.pack(anchor=tk.W, pady=(0, 10))

    def _build_filter_tab(self) -> None:
        # 1. Levels and keywords Frame
        box_frame = ttk.LabelFrame(self.tab_filter, text="Levels and keywords", padding=6)
        box_frame.pack(fill=tk.X, pady=(0, 8))

        col1 = ttk.Frame(box_frame)
        col1.pack(side=tk.LEFT, padx=(4, 16), anchor=tk.N)

        self.var_all_levels = tk.BooleanVar(value=True)
        ttk.Checkbutton(col1, text="All levels", variable=self.var_all_levels).pack(anchor=tk.W, pady=1)

        self.level_checks = {}
        for lvl in ["Information", "Warning", "Error", "Critical", "Verbose"]:
            v = tk.BooleanVar(value=False)
            ttk.Checkbutton(col1, text=lvl, variable=v).pack(anchor=tk.W, padx=14, pady=1)
            self.level_checks[lvl] = v

        col2 = ttk.Frame(box_frame)
        col2.pack(side=tk.LEFT, padx=16, anchor=tk.N)

        self.var_all_kw = tk.BooleanVar(value=True)
        ttk.Checkbutton(col2, text="All keywords", variable=self.var_all_kw).pack(anchor=tk.W, pady=1)

        for kw in ["Audit Failure", "Audit Success", "Correlation Hint", "EventLog Classic"]:
            ttk.Checkbutton(col2, text=kw).pack(anchor=tk.W, padx=14, pady=1)

        col3 = ttk.Frame(box_frame)
        col3.pack(side=tk.LEFT, padx=16, anchor=tk.N)
        for kw in ["Response Time", "Sqm", "Wdi Context", "Wdi Diagnostic"]:
            ttk.Checkbutton(col3, text=kw).pack(anchor=tk.W, pady=1)

        # 2. Event Source(s)
        src_row = ttk.Frame(self.tab_filter)
        src_row.pack(fill=tk.X, pady=4)
        ttk.Label(src_row, text="Event Source(s):", width=14).pack(side=tk.LEFT)
        self.entry_src = ttk.Entry(src_row, width=35)
        self.entry_src.pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(src_row, text="...", width=3).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(src_row, text="Exclude").pack(side=tk.LEFT)

        # 3. Event ID(s)
        id_row = ttk.Frame(self.tab_filter)
        id_row.pack(fill=tk.X, pady=4)
        ttk.Label(id_row, text="Event ID(s):", width=14).pack(side=tk.LEFT)
        self.entry_ids = ttk.Entry(id_row, width=35)
        self.entry_ids.pack(side=tk.LEFT)

        subtext = ttk.Label(
            self.tab_filter,
            text="Enter ID numbers and/or ID ranges, separated by comas, use exclamation mark to exclude criteria (e.g. 1-19,100,250-450!10,255)",
            font=("Segoe UI", 7),
            foreground="#666666"
        )
        subtext.pack(anchor=tk.W, pady=(0, 6))

        # 4. Time frame & Test query
        time_row = ttk.Frame(self.tab_filter)
        time_row.pack(fill=tk.X, pady=4)

        self.var_get_events = tk.BooleanVar(value=False)
        ttk.Checkbutton(time_row, text="Get events for the last", variable=self.var_get_events).pack(side=tk.LEFT)
        
        sp_days = ttk.Spinbox(time_row, from_=0, to=365, width=4)
        sp_days.set(7)
        sp_days.pack(side=tk.LEFT, padx=3)
        ttk.Label(time_row, text="days").pack(side=tk.LEFT, padx=2)

        sp_hrs = ttk.Spinbox(time_row, from_=0, to=23, width=3)
        sp_hrs.set(0)
        sp_hrs.pack(side=tk.LEFT, padx=3)
        ttk.Label(time_row, text="hours").pack(side=tk.LEFT, padx=2)

        sp_mins = ttk.Spinbox(time_row, from_=0, to=59, width=3)
        sp_mins.set(0)
        sp_mins.pack(side=tk.LEFT, padx=3)
        ttk.Label(time_row, text="minutes").pack(side=tk.LEFT, padx=2)

        btn_test = ttk.Button(time_row, text="Test query", width=12)
        btn_test.pack(side=tk.RIGHT)

        # 5. XML Query Box
        xml_frame = ttk.Frame(self.tab_filter)
        xml_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.txt_query = tk.Text(
            xml_frame,
            height=6,
            wrap=tk.NONE,
            font=("Consolas", 8),
            bg="#FAFAFA",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.txt_query.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_side = ttk.Frame(xml_frame)
        btn_side.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))
        ttk.Button(btn_side, text="Load", width=7).pack(pady=2)
        ttk.Button(btn_side, text="Save", width=7).pack(pady=2)
        ttk.Button(btn_side, text="Clear", width=7, command=lambda: self.txt_query.delete("1.0", tk.END)).pack(pady=2)

    def _load_template_data(self) -> None:
        self.entry_task_name.insert(0, self.template.name)
        self.txt_template_desc.insert("1.0", self.template.description)
        self.entry_ids.insert(0, ",".join(str(i) for i in self.template.event_ids))
        self.txt_query.insert("1.0", self.template.xml_query)

    def _shift_tab(self, direction: int) -> None:
        curr = self.nb.index(self.nb.select())
        new_idx = max(0, min(4, curr + direction))
        self.nb.select(new_idx)

    def _do_finish(self) -> None:
        raw_ids = self.entry_ids.get().strip()
        ids = [int(i.strip()) for i in raw_ids.split(",") if i.strip().isdigit()]
        self.template.event_ids = ids
        self.template.target_channel = self.entry_channel.get().strip() or "Security"
        self.on_finish(self.template, self.entry_task_name.get().strip() or self.template.name)
        self.destroy()
