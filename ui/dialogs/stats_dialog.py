"""
Event Log Explorer - Statistics & Analytics Dashboard
Displays comprehensive triage metrics, top event IDs, and source breakdowns.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
from backend.models import EventRecord
from backend.analytics import LogAnalytics


class StatsDialog(tk.Toplevel):
    """Visual statistics and incident summary dialog."""

    def __init__(self, parent: tk.Widget, records: List[EventRecord], title_prefix: str = "Log"):
        super().__init__(parent)
        self.title(f"Log Statistics & Analytical Summary - {title_prefix}")
        self.geometry("780x600")
        self.transient(parent)
        self.grab_set()

        self.records = records
        self.summary = LogAnalytics.generate_summary(records)

        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Metric Cards Frame
        cards_frame = ttk.LabelFrame(main_frame, text="Summary Metrics", padding=8)
        cards_frame.pack(fill=tk.X, pady=(0, 10))

        tot = self.summary["total"]
        lvls = self.summary["levels"]
        errs = lvls.get("Error", 0) + lvls.get("Critical", 0)
        warns = lvls.get("Warning", 0)
        audit_fails = lvls.get("Audit Failure", 0)
        infos = lvls.get("Information", 0) + lvls.get("Audit Success", 0)

        metrics = [
            ("TOTAL EVENTS", tot, "#0284c7"),
            ("ERRORS / CRITICAL", errs, "#dc2626"),
            ("WARNINGS", warns, "#d97706"),
            ("AUDIT FAILURES", audit_fails, "#be185d"),
            ("INFORMATION / SUCCESS", infos, "#16a34a"),
        ]

        for idx, (lbl, val, col) in enumerate(metrics):
            card = tk.Frame(cards_frame, bg="white", relief=tk.SOLID, borderwidth=1, padx=12, pady=6)
            card.grid(row=0, column=idx, padx=4, pady=2, sticky="nsew")
            cards_frame.grid_columnconfigure(idx, weight=1)

            tk.Label(card, text=lbl, bg="white", fg="#64748b", font=("Segoe UI", 8, "bold")).pack()
            tk.Label(card, text=str(val), bg="white", fg=col, font=("Segoe UI", 16, "bold")).pack()

        # 2. Notebook with detailed tables
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Tab: Top Event IDs
        tab_ids = ttk.Frame(notebook)
        notebook.add(tab_ids, text="  🔢 Top Event IDs  ")
        self._build_ids_tab(tab_ids)

        # Tab: Top Sources
        tab_src = ttk.Frame(notebook)
        notebook.add(tab_src, text="  🏢 Top Event Sources  ")
        self._build_sources_tab(tab_src)

        # Tab: Top Users
        tab_usr = ttk.Frame(notebook)
        notebook.add(tab_usr, text="  👤 Top Users  ")
        self._build_users_tab(tab_usr)

        # Bottom Bar
        b_box = ttk.Frame(main_frame)
        b_box.pack(fill=tk.X)

        ttk.Button(b_box, text="Close", command=self.destroy).pack(side=tk.RIGHT)

    def _build_ids_tab(self, parent: ttk.Frame) -> None:
        tree_frame = ttk.Frame(parent, padding=4)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("EventID", "Count", "Percentage", "Description")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        
        tree.heading("EventID", text="Event ID")
        tree.heading("Count", text="Occurrences")
        tree.heading("Percentage", text="% Total")
        tree.heading("Description", text="Event Meaning / Known Description")

        tree.column("EventID", width=80, anchor=tk.CENTER)
        tree.column("Count", width=100, anchor=tk.CENTER)
        tree.column("Percentage", width=90, anchor=tk.CENTER)
        tree.column("Description", width=420, anchor=tk.W)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        for item in self.summary["top_event_ids"]:
            tree.insert("", "end", values=(
                item["event_id"],
                item["count"],
                f"{item['percentage']}%",
                item["description"]
            ))

    def _build_sources_tab(self, parent: ttk.Frame) -> None:
        tree_frame = ttk.Frame(parent, padding=4)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("Source", "Count", "Percentage")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        
        tree.heading("Source", text="Provider / Event Source")
        tree.heading("Count", text="Event Count")
        tree.heading("Percentage", text="% Total")

        tree.column("Source", width=420, anchor=tk.W)
        tree.column("Count", width=120, anchor=tk.CENTER)
        tree.column("Percentage", width=100, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        for item in self.summary["top_sources"]:
            tree.insert("", "end", values=(
                item["source"],
                item["count"],
                f"{item['percentage']}%"
            ))

    def _build_users_tab(self, parent: ttk.Frame) -> None:
        tree_frame = ttk.Frame(parent, padding=4)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("User", "Count", "Percentage")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        
        tree.heading("User", text="User Account / Domain Identity")
        tree.heading("Count", text="Event Count")
        tree.heading("Percentage", text="% Total")

        tree.column("User", width=420, anchor=tk.W)
        tree.column("Count", width=120, anchor=tk.CENTER)
        tree.column("Percentage", width=100, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        for item in self.summary["top_users"]:
            tree.insert("", "end", values=(
                item["user"],
                item["count"],
                f"{item['percentage']}%"
            ))
