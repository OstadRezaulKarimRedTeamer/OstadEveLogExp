"""
Event Log Explorer - Export Dialog
Allows exporting events to CSV, JSON, XML, or Standalone HTML Report.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
import os
from backend.models import EventRecord
from backend.exporter import EventExporter


class ExportDialog(tk.Toplevel):
    """Export configuration dialog."""

    def __init__(self, parent: tk.Widget, all_records: List[EventRecord], filtered_records: List[EventRecord], default_name: str = "EventLog"):
        super().__init__(parent)
        self.title("Export Event Log - Event Log Explorer")
        self.geometry("480x360")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.all_records = all_records
        self.filtered_records = filtered_records
        self.default_name = default_name

        self._build_ui()

    def _build_ui(self) -> None:
        f = ttk.Frame(self, padding=14)
        f.pack(fill=tk.BOTH, expand=True)

        # 1. Scope selection
        scope_frame = ttk.LabelFrame(f, text="Export Scope", padding=8)
        scope_frame.pack(fill=tk.X, pady=(0, 10))

        self.scope_var = tk.StringVar(value="filtered")
        ttk.Radiobutton(
            scope_frame,
            text=f"Filtered Events View ({len(self.filtered_records)} records)",
            variable=self.scope_var,
            value="filtered"
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(
            scope_frame,
            text=f"All Loaded Events ({len(self.all_records)} records)",
            variable=self.scope_var,
            value="all"
        ).pack(anchor=tk.W, pady=2)

        # 2. Format selection
        fmt_frame = ttk.LabelFrame(f, text="File Format", padding=8)
        fmt_frame.pack(fill=tk.X, pady=(0, 10))

        self.fmt_var = tk.StringVar(value="html")
        formats = [
            ("html", "Interactive HTML Web Report (.html) - Recommended"),
            ("csv", "Comma Separated Values (.csv) - Excel Compatible"),
            ("json", "JavaScript Object Notation (.json)"),
            ("xml", "Raw Event Log XML (.xml)")
        ]
        for val, desc in formats:
            ttk.Radiobutton(fmt_frame, text=desc, variable=self.fmt_var, value=val).pack(anchor=tk.W, pady=2)

        # Bottom Buttons
        btn_box = ttk.Frame(f)
        btn_box.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_box, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_box, text="💾 Save / Export...", command=self._do_export).pack(side=tk.RIGHT)

    def _do_export(self) -> None:
        fmt = self.fmt_var.get()
        records_to_export = self.filtered_records if self.scope_var.get() == "filtered" else self.all_records
        
        if not records_to_export:
            messagebox.showwarning("Export Warning", "No records available to export.", parent=self)
            return

        ext_map = {
            "html": ("HTML Files", "*.html"),
            "csv": ("CSV Files", "*.csv"),
            "json": ("JSON Files", "*.json"),
            "xml": ("XML Files", "*.xml")
        }
        
        filetypes = [ext_map[fmt], ("All Files", "*.*")]
        init_file = f"{self.default_name}_export.{fmt}"

        save_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Exported Log As",
            initialfile=init_file,
            filetypes=filetypes
        )

        if not save_path:
            return

        try:
            if fmt == "html":
                EventExporter.export_html_report(records_to_export, save_path, title=f"Event Log - {self.default_name}")
            elif fmt == "csv":
                EventExporter.export_csv(records_to_export, save_path)
            elif fmt == "json":
                EventExporter.export_json(records_to_export, save_path)
            elif fmt == "xml":
                EventExporter.export_xml(records_to_export, save_path)

            messagebox.showinfo(
                "Export Complete",
                f"Successfully exported {len(records_to_export)} events to:\n{save_path}",
                parent=self
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}", parent=self)
