"""
Event Log Explorer - Standalone Event Properties Dialog
Popup dialog providing full view and navigation (Next/Prev) for an event.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
import urllib.parse
from typing import List, Callable
from backend.models import EventRecord
from backend.log_reader import format_event_description


class EventPropertiesDialog(tk.Toplevel):
    """Full-featured standalone event properties dialog."""

    def __init__(
        self,
        parent: tk.Widget,
        records: List[EventRecord],
        current_index: int,
        on_bookmark_toggle: Callable[[EventRecord], None]
    ):
        super().__init__(parent)
        self.records = records
        self.idx = current_index
        self.on_bookmark_toggle = on_bookmark_toggle

        self.geometry("680x620")
        self.transient(parent)

        self._build_ui()
        self._load_event()

    def _build_ui(self) -> None:
        f = ttk.Frame(self, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        # Top Header Box
        header_frame = ttk.LabelFrame(f, text="Event Summary", padding=8)
        header_frame.pack(fill=tk.X, pady=(0, 6))

        self.prop_labels = {}
        fields = [
            ("Event ID:", 0, 0), ("Level:", 0, 2), ("Date & Time:", 0, 4),
            ("Source:", 1, 0), ("User:", 1, 2), ("Task Category:", 1, 4),
            ("Computer:", 2, 0), ("Record ID:", 2, 2), ("Keywords:", 2, 4),
        ]
        for text, r, c in fields:
            lbl_t = ttk.Label(header_frame, text=text, font=("Segoe UI", 9, "bold"))
            lbl_t.grid(row=r, column=c, sticky=tk.W, padx=(4, 2), pady=2)
            lbl_v = ttk.Label(header_frame, text="-", font=("Segoe UI", 9))
            lbl_v.grid(row=r, column=c + 1, sticky=tk.W, padx=(0, 8), pady=2)
            self.prop_labels[text] = lbl_v

        # Tabs: Description, XML, EventData
        nb = ttk.Notebook(f)
        nb.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Description Tab
        tab_desc = ttk.Frame(nb, padding=4)
        nb.add(tab_desc, text=" Description ")
        self.txt_desc = tk.Text(tab_desc, wrap=tk.WORD, font=("Consolas", 10), bg="#FFFFFF", padx=8, pady=8)
        d_vsb = ttk.Scrollbar(tab_desc, orient="vertical", command=self.txt_desc.yview)
        self.txt_desc.configure(yscrollcommand=d_vsb.set)
        self.txt_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        d_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # XML Tab
        tab_xml = ttk.Frame(nb, padding=4)
        nb.add(tab_xml, text=" XML View ")
        self.txt_xml = tk.Text(tab_xml, wrap=tk.NONE, font=("Consolas", 9), bg="#FAFAFA", padx=8, pady=8)
        x_vsb = ttk.Scrollbar(tab_xml, orient="vertical", command=self.txt_xml.yview)
        x_hsb = ttk.Scrollbar(tab_xml, orient="horizontal", command=self.txt_xml.xview)
        self.txt_xml.configure(yscrollcommand=x_vsb.set, xscrollcommand=x_hsb.set)
        self.txt_xml.grid(row=0, column=0, sticky="nsew")
        x_vsb.grid(row=0, column=1, sticky="ns")
        x_hsb.grid(row=1, column=0, sticky="ew")
        tab_xml.grid_rowconfigure(0, weight=1)
        tab_xml.grid_columnconfigure(0, weight=1)

        # Bottom navigation and action bar
        bar = ttk.Frame(f)
        bar.pack(fill=tk.X)

        self.btn_prev = ttk.Button(bar, text="◀ Previous", command=self._prev_event)
        self.btn_prev.pack(side=tk.LEFT, padx=2)

        self.btn_next = ttk.Button(bar, text="Next ▶", command=self._next_event)
        self.btn_next.pack(side=tk.LEFT, padx=2)

        self.btn_bkm = ttk.Button(bar, text="⭐ Bookmark", command=self._toggle_bookmark)
        self.btn_bkm.pack(side=tk.LEFT, padx=6)

        ttk.Button(bar, text="🌐 Lookup Online", command=self._lookup_online).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bar, text="📋 Copy Text", command=self._copy_text).pack(side=tk.RIGHT, padx=2)

    def _load_event(self) -> None:
        if not (0 <= self.idx < len(self.records)):
            return
        rec = self.records[self.idx]
        self.title(f"Event Properties - Event {rec.event_id} ({rec.level_name}) [{self.idx + 1} of {len(self.records)}]")

        self.prop_labels["Event ID:"].config(text=str(rec.event_id))
        self.prop_labels["Level:"].config(text=rec.level_name)
        self.prop_labels["Date & Time:"].config(text=rec.time_created_str)
        self.prop_labels["Source:"].config(text=rec.provider_name)
        self.prop_labels["User:"].config(text=rec.user_name)
        self.prop_labels["Task Category:"].config(text=rec.task_category)
        self.prop_labels["Computer:"].config(text=rec.computer)
        self.prop_labels["Record ID:"].config(text=str(rec.record_id))
        self.prop_labels["Keywords:"].config(text=rec.keywords)

        desc = format_event_description(rec.provider_name, rec.handle, rec.event_data)
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", desc)

        self.txt_xml.delete("1.0", tk.END)
        self.txt_xml.insert("1.0", rec.xml_raw)

        self.btn_bkm.config(text="⭐ Remove Bookmark" if rec.bookmarked else "⭐ Bookmark")
        self.btn_prev.config(state=tk.NORMAL if self.idx > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.idx < len(self.records) - 1 else tk.DISABLED)

    def _prev_event(self) -> None:
        if self.idx > 0:
            self.idx -= 1
            self._load_event()

    def _next_event(self) -> None:
        if self.idx < len(self.records) - 1:
            self.idx += 1
            self._load_event()

    def _toggle_bookmark(self) -> None:
        rec = self.records[self.idx]
        rec.bookmarked = not rec.bookmarked
        self.on_bookmark_toggle(rec)
        self._load_event()

    def _lookup_online(self) -> None:
        rec = self.records[self.idx]
        q = urllib.parse.quote(f"Windows Event ID {rec.event_id} {rec.provider_name}")
        webbrowser.open(f"https://www.google.com/search?q={q}")

    def _copy_text(self) -> None:
        txt = self.txt_desc.get("1.0", tk.END).strip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
