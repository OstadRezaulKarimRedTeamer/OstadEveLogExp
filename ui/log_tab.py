"""
Event Log Explorer - Log Tab (Grid View matching Screenshot 1)
Features:
- Sub-toolbar: |<, <, >, >|, Refresh, Total Count (8943), Filtered Count (8711), Selected (1), Timezone
- Exact columns: Type, Date, Time, Event, Source, Category, User, Channel, Computer
- Split preview: Description and Data tabs
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timezone
from typing import List, Optional, Callable, Dict, Any
from backend.models import EventRecord, FilterCriteria
from backend.log_reader import LogReader
from backend.filter_engine import FilterEngine, parse_id_ranges
from backend.color_engine import ColorEngine
from ui.details_pane import DetailsPane
from ui.dialogs.filter_dialog import FilterDialog
from ui.dialogs.event_details_dialog import EventPropertiesDialog


# Exact icons matching Screenshot 1
LEVEL_ICONS = {
    "Critical": "⛔ Critical",
    "Error": "❌ Error",
    "Warning": "⚠️ Warning",
    "Information": "ℹ Information",
    "Audit Success": "🔑 Audit Success",
    "Audit Failure": "🚫 Audit Failure",
    "Verbose": "💬 Verbose"
}


class LogTab(ttk.Frame):
    """Log viewer tab matching Screenshot 1 & 3."""

    def __init__(
        self,
        parent: tk.Widget,
        log_source: str,
        is_file: bool,
        color_engine: ColorEngine,
        computer_name: str = "",
        on_bookmark_changed: Optional[Callable[[EventRecord], None]] = None,
        on_status_update: Optional[Callable[[str], None]] = None,
        on_open_analytics: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.log_source = log_source
        self.is_file = is_file
        self.color_engine = color_engine
        self.computer_name = computer_name or "LocalPC"
        self.on_bookmark_changed = on_bookmark_changed
        self.on_status_update = on_status_update
        self.on_open_analytics = on_open_analytics

        self.all_records: List[EventRecord] = []
        self.filtered_records: List[EventRecord] = []
        self.criteria = FilterCriteria()
        self.sort_column = "Date"
        self.sort_descending = True
        self.is_loading = False

        self._build_ui()
        self.load_log()

    def _build_ui(self) -> None:
        # 1. Sub-Toolbar immediately above Table (Matches Screenshot 1!)
        self._build_navigation_strip()

        # 2. Main Vertical PanedWindow (Table on Top, Description Pane on Bottom)
        self.paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Top Pane: Events Table
        table_frame = ttk.Frame(self.paned)
        self._build_table(table_frame)
        self.paned.add(table_frame, weight=3)

        # Bottom Pane: Details Pane (with Description and Data tabs)
        self.details_pane = DetailsPane(self.paned, on_close=self._toggle_details_pane)
        self.paned.add(self.details_pane, weight=1)

    def _build_navigation_strip(self) -> None:
        strip = tk.Frame(self, bg="#F5F5F5", height=28, relief=tk.FLAT, bd=0)
        strip.pack(fill=tk.X, side=tk.TOP, padx=2, pady=1)

        # Paging Buttons: |<, <, >, >|, Refresh
        btn_first = tk.Button(strip, text="|<", font=("Segoe UI", 8), bg="#F5F5F5", bd=1, padx=4, command=self._goto_first)
        btn_first.pack(side=tk.LEFT, padx=1)

        btn_prev = tk.Button(strip, text="<", font=("Segoe UI", 8), bg="#F5F5F5", bd=1, padx=4, command=self._goto_prev)
        btn_prev.pack(side=tk.LEFT, padx=1)

        btn_next = tk.Button(strip, text=">", font=("Segoe UI", 8), bg="#F5F5F5", bd=1, padx=4, command=self._goto_next)
        btn_next.pack(side=tk.LEFT, padx=1)

        btn_last = tk.Button(strip, text=">|", font=("Segoe UI", 8), bg="#F5F5F5", bd=1, padx=4, command=self._goto_last)
        btn_last.pack(side=tk.LEFT, padx=1)

        btn_refresh = tk.Button(strip, text="🔄", font=("Segoe UI", 8), bg="#F5F5F5", bd=1, padx=4, command=self.load_log)
        btn_refresh.pack(side=tk.LEFT, padx=(2, 10))

        # Counter Badges (Matching Screenshot 1: 8943, 8711, 1)
        self.lbl_tot_badge = tk.Label(strip, text="🔄 0", bg="#F5F5F5", fg="#005A9E", font=("Segoe UI", 9, "bold"))
        self.lbl_tot_badge.pack(side=tk.LEFT, padx=6)

        self.lbl_filt_badge = tk.Label(strip, text="▽ 0", bg="#F5F5F5", fg="#107C41", font=("Segoe UI", 9, "bold"))
        self.lbl_filt_badge.pack(side=tk.LEFT, padx=6)

        self.lbl_sel_badge = tk.Label(strip, text="☑ 0", bg="#F5F5F5", fg="#333333", font=("Segoe UI", 9))
        self.lbl_sel_badge.pack(side=tk.LEFT, padx=6)

        # Right side: Timezone & Analytics icon
        btn_dropdown = tk.Button(strip, text="▼", font=("Segoe UI", 7), bg="#F5F5F5", bd=0, padx=4)
        btn_dropdown.pack(side=tk.RIGHT, padx=2)

        btn_analytics = tk.Button(
            strip,
            text="📊",
            font=("Segoe UI", 9),
            bg="#F5F5F5",
            bd=0,
            padx=4,
            command=self._open_analytics_handler
        )
        btn_analytics.pack(side=tk.RIGHT, padx=4)

        # Timezone label (e.g. UTC+06:00)
        local_tz = datetime.now().astimezone().strftime("UTC%z")
        formatted_tz = f"{local_tz[:6]}:{local_tz[6:]}" if len(local_tz) >= 5 else local_tz
        lbl_tz = tk.Label(strip, text=formatted_tz, bg="#F5F5F5", fg="#555555", font=("Segoe UI", 8))
        lbl_tz.pack(side=tk.RIGHT, padx=10)

    def _build_table(self, parent: ttk.Frame) -> None:
        # Exact columns matching Screenshot 1:
        # Type, Date, Time, Event, Source, Category, User, Channel, Computer
        self.cols = ("Type", "Date", "Time", "Event", "Source", "Category", "User", "Channel", "Computer")
        self.tree = ttk.Treeview(parent, columns=self.cols, show="headings", selectmode="browse")

        col_widths = {
            "Type": 125,
            "Date": 85,
            "Time": 75,
            "Event": 55,
            "Source": 175,
            "Category": 105,
            "User": 130,
            "Channel": 80,
            "Computer": 95
        }

        for col in self.cols:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=col_widths.get(col, 100), anchor=tk.W)

        self.tree.column("Event", anchor=tk.CENTER)
        self.tree.column("Date", anchor=tk.CENTER)
        self.tree.column("Time", anchor=tk.CENTER)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)
        self.tree.bind("<Double-1>", self._on_row_double_click)
        self.tree.bind("<Return>", self._on_row_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=False)
        self.context_menu.add_command(label="Event Properties... (Double Click)", command=self._open_properties)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Filter by this Event ID", command=self._filter_by_selected_id)
        self.context_menu.add_command(label="Filter by this Source", command=self._filter_by_selected_source)
        self.context_menu.add_command(label="Exclude this Event ID", command=self._exclude_selected_id)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="⭐ Toggle Bookmark", command=self._toggle_selected_bookmark)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy Row Values", command=self._copy_selected_row)
        self.context_menu.add_command(label="📋 Copy Event XML", command=self._copy_selected_xml)

    def load_log(self, max_records: int = 5000) -> None:
        if self.is_loading:
            return
            
        self.is_loading = True
        if self.on_status_update:
            self.on_status_update(f"Reading '{self.log_source}'...")

        self.tree.delete(*self.tree.get_children())
        self.details_pane.display_record(None)

        def worker():
            try:
                records = LogReader.read_events(
                    source_path=self.log_source,
                    is_file=self.is_file,
                    max_events=max_records,
                    reverse=True
                )
                # Ensure computer is attributed
                if self.computer_name:
                    for r in records:
                        if not r.computer or r.computer == "Localhost":
                            r.computer = self.computer_name

                self.after(0, lambda: self._on_load_complete(records))
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda: self._on_load_error(err_msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_load_complete(self, records: List[EventRecord]) -> None:
        self.all_records = records
        self.is_loading = False
        self._refresh_table()
        if self.on_status_update:
            self.on_status_update(f"Loaded {len(records)} events from '{self.log_source}'.")

    def _on_load_error(self, err_msg: str) -> None:
        self.is_loading = False
        messagebox.showerror("Error Opening Log", f"Failed to open '{self.log_source}':\n{err_msg}", parent=self)

    def _refresh_table(self) -> None:
        self.filtered_records = FilterEngine.filter_records(self.all_records, self.criteria)
        self.tree.delete(*self.tree.get_children())

        # Update Badges (Screenshot 1: 8943, 8711, 1)
        self.lbl_tot_badge.config(text=f"🔄 {len(self.all_records)}")
        self.lbl_filt_badge.config(text=f"▽ {len(self.filtered_records)}")

        # Configure color tags
        for rule in self.color_engine.rules:
            if rule.enabled:
                self.tree.tag_configure(
                    f"tag_{rule.rule_id}",
                    background=rule.bg_color,
                    foreground=rule.fg_color
                )

        # Highlight warning, error rows
        self.tree.tag_configure("tag_warning_row", background="#FFFBEA", foreground="#000000")
        self.tree.tag_configure("tag_error_row", background="#FFEEEE", foreground="#900C3F")
        self.tree.tag_configure("tag_audit_row", background="#F0FFF4", foreground="#117A65")

        for idx, r in enumerate(self.filtered_records):
            tag_to_apply = ""
            for rule in self.color_engine.rules:
                if not rule.enabled:
                    continue
                matched = False
                val = ""
                if rule.match_field == "Level":
                    val = r.level_name
                elif rule.match_field == "EventID":
                    val = str(r.event_id)
                elif rule.match_field == "Source":
                    val = r.provider_name
                elif rule.match_field == "User":
                    val = r.user_name

                if rule.match_op == "equals" and val.strip().lower() == rule.match_val.strip().lower():
                    matched = True
                elif rule.match_op == "contains" and rule.match_val.strip().lower() in val.strip().lower():
                    matched = True

                if matched:
                    tag_to_apply = f"tag_{rule.rule_id}"
                    break

            if not tag_to_apply:
                if r.level_name == "Warning":
                    tag_to_apply = "tag_warning_row"
                elif r.level_name in ("Error", "Critical"):
                    tag_to_apply = "tag_error_row"
                elif r.level_name == "Audit Success":
                    tag_to_apply = "tag_audit_row"

            tags = (tag_to_apply,) if tag_to_apply else ()

            lvl_display = LEVEL_ICONS.get(r.level_name, r.level_name)

            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(
                    lvl_display,
                    r.date_str,
                    r.time_str,
                    r.event_id,
                    r.provider_name,
                    r.task_category,
                    r.user_name,
                    r.channel,
                    r.computer
                ),
                tags=tags
            )

        if self.filtered_records:
            self.tree.selection_set("0")
            self.tree.focus("0")
            self.details_pane.display_record(self.filtered_records[0])
            self.lbl_sel_badge.config(text="☑ 1")
        else:
            self.lbl_sel_badge.config(text="☑ 0")

    def _sort_by_column(self, col: str) -> None:
        if self.sort_column == col:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = col
            self.sort_descending = False

        # Update sort arrow in header
        for c in self.cols:
            header_text = c + (" ▽" if self.sort_descending else " △") if c == col else c
            self.tree.heading(c, text=header_text)

        def get_sort_key(record: EventRecord):
            if col == "Date" or col == "Time":
                return record.time_created or datetime.min
            elif col == "Event":
                return record.event_id
            elif col == "Type":
                return record.level_name
            elif col == "Source":
                return record.provider_name.lower()
            elif col == "User":
                return record.user_name.lower()
            elif col == "Category":
                return record.task_category.lower()
            elif col == "Channel":
                return record.channel.lower()
            elif col == "Computer":
                return record.computer.lower()
            return record.description.lower()

        self.filtered_records.sort(key=get_sort_key, reverse=self.sort_descending)
        self._refresh_table()

    def _on_row_selected(self, event) -> None:
        sel = self.tree.selection()
        if not sel:
            self.lbl_sel_badge.config(text="☑ 0")
            return
        self.lbl_sel_badge.config(text=f"☑ {len(sel)}")
        idx = int(sel[0])
        if 0 <= idx < len(self.filtered_records):
            self.details_pane.display_record(self.filtered_records[idx])

    def _on_row_double_click(self, event) -> None:
        self._open_properties()

    def _on_right_click(self, event) -> None:
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._on_row_selected(None)
            self.context_menu.post(event.x_root, event.y_root)

    def _open_properties(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        EventPropertiesDialog(
            parent=self,
            records=self.filtered_records,
            current_index=idx,
            on_bookmark_toggle=lambda rec: None
        )

    def _goto_first(self) -> None:
        if self.filtered_records:
            self.tree.selection_set("0")
            self.tree.see("0")
            self._on_row_selected(None)

    def _goto_last(self) -> None:
        if self.filtered_records:
            last = str(len(self.filtered_records) - 1)
            self.tree.selection_set(last)
            self.tree.see(last)
            self._on_row_selected(None)

    def _goto_prev(self) -> None:
        sel = self.tree.selection()
        if sel:
            curr = int(sel[0])
            if curr > 0:
                nxt = str(curr - 1)
                self.tree.selection_set(nxt)
                self.tree.see(nxt)
                self._on_row_selected(None)

    def _goto_next(self) -> None:
        sel = self.tree.selection()
        if sel:
            curr = int(sel[0])
            if curr < len(self.filtered_records) - 1:
                nxt = str(curr + 1)
                self.tree.selection_set(nxt)
                self.tree.see(nxt)
                self._on_row_selected(None)

    def _filter_by_selected_id(self) -> None:
        rec = self.details_pane.current_record
        if rec:
            self.criteria.event_ids_include = [rec.event_id]
            self._refresh_table()

    def _filter_by_selected_source(self) -> None:
        rec = self.details_pane.current_record
        if rec:
            self.criteria.sources_include = [rec.provider_name]
            self._refresh_table()

    def _exclude_selected_id(self) -> None:
        rec = self.details_pane.current_record
        if rec:
            if rec.event_id not in self.criteria.event_ids_exclude:
                self.criteria.event_ids_exclude.append(rec.event_id)
                self._refresh_table()

    def _toggle_selected_bookmark(self) -> None:
        rec = self.details_pane.current_record
        if rec:
            rec.bookmarked = not rec.bookmarked

    def _copy_selected_row(self) -> None:
        rec = self.details_pane.current_record
        if rec:
            line = f"{rec.level_name}\t{rec.date_str}\t{rec.time_str}\t{rec.event_id}\t{rec.provider_name}\t{rec.task_category}\t{rec.user_name}\t{rec.channel}\t{rec.computer}\t{rec.description}"
            self.clipboard_clear()
            self.clipboard_append(line)

    def _copy_selected_xml(self) -> None:
        rec = self.details_pane.current_record
        if rec:
            self.clipboard_clear()
            self.clipboard_append(rec.xml_raw)

    def _toggle_details_pane(self) -> None:
        if self.details_pane.winfo_ismapped():
            self.paned.forget(self.details_pane)
        else:
            self.paned.add(self.details_pane, weight=1)

    def _open_analytics_handler(self) -> None:
        if self.on_open_analytics:
            self.on_open_analytics()
