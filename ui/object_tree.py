"""
Event Log Explorer - Objects Tree Sidebar
Matches the exact tree structure from Screenshot 1 & 2.
"""

import tkinter as tk
from tkinter import ttk
import os
from typing import Callable, Optional, Dict
from backend.channel_manager import ChannelManager
from backend.templates import TASK_TEMPLATES, TaskTemplate


class ObjectTree(ttk.Frame):
    """Sidebar tree matching Screenshot 1 & 2."""

    def __init__(
        self,
        parent: tk.Widget,
        on_channel_selected: Callable[[str, bool, str], None], # (channel, new_tab, computer)
        on_open_file_requested: Callable[[], None],
        on_template_selected: Callable[[TaskTemplate], None],
        on_close_sidebar: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.on_channel_selected = on_channel_selected
        self.on_open_file_requested = on_open_file_requested
        self.on_template_selected = on_template_selected
        self.on_close_sidebar = on_close_sidebar

        self._build_ui()
        self._populate_tree()

    def _build_ui(self) -> None:
        # 1. Header Bar: "Objects tree" with '✕' close button
        header_bar = tk.Frame(self, bg="#F0F0F0", height=24)
        header_bar.pack(fill=tk.X, padx=2, pady=(1, 2))

        lbl = tk.Label(header_bar, text="Objects tree", bg="#F0F0F0", font=("Segoe UI", 9, "bold"))
        lbl.pack(side=tk.LEFT, padx=4)

        if self.on_close_sidebar:
            btn_x = tk.Button(
                header_bar,
                text="✕",
                font=("Segoe UI", 8),
                bg="#F0F0F0",
                relief=tk.FLAT,
                bd=0,
                padx=4,
                command=self.on_close_sidebar
            )
            btn_x.pack(side=tk.RIGHT, padx=2)

        # 2. Search Field: "Search [                 ]"
        search_frame = ttk.Frame(self, padding=(4, 2, 4, 4))
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="Search", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_tree())
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 3. Main Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0, 2))

        self.tree = ttk.Treeview(tree_frame, selectmode="browse", show="tree")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Bindings
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=False)
        self.context_menu.add_command(label="Open in New Tab", command=self._menu_open_new_tab)
        self.context_menu.add_command(label="Open in Current Tab", command=self._menu_open_current_tab)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Refresh Tree", command=self._populate_tree)

    def _populate_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        comp_name = os.environ.get("COMPUTERNAME", "LocalPC")

        # 1. Local Computer (Matches "MIKE-LN (local)" in screenshot)
        local_id = self.tree.insert("", "end", text=f"🖥️ {comp_name} (local)", open=True)

        categorized = ChannelManager.get_categorized_channels()

        # Windows Logs
        win_id = self.tree.insert(local_id, "end", text="📁 Windows Logs", open=True)
        for ch in categorized["Windows Logs"]:
            self.tree.insert(win_id, "end", text=f"📄 {ch}", values=(ch, "channel", comp_name))

        # Applications & Services Logs
        app_id = self.tree.insert(local_id, "end", text="📁 Applications and Services Logs", open=False)
        for ch in categorized["Popular Diagnostic Logs"]:
            self.tree.insert(app_id, "end", text=f"📄 {ch}", values=(ch, "channel", comp_name))
        for ch in categorized["Applications and Services Logs"][:100]:
            self.tree.insert(app_id, "end", text=f"📄 {ch}", values=(ch, "channel", comp_name))

        # 2. Remote Computers (Matches Screenshot 1)
        for remote_comp in ["VM7", "WINDEV2407EVAL", "SRV002", "VM11", "DATA", "ARMPC", "192.168.1.165 (ARMPC)"]:
            r_id = self.tree.insert("", "end", text=f"🖥️ {remote_comp}", open=False)
            self.tree.insert(r_id, "end", text="📄 System", values=("System", "channel", remote_comp))
            self.tree.insert(r_id, "end", text="📄 Security", values=("Security", "channel", remote_comp))
            self.tree.insert(r_id, "end", text="📄 Application", values=("Application", "channel", remote_comp))

        # 3. Log Files
        log_files_id = self.tree.insert("", "end", text="📁 Log Files", open=True)
        self.tree.insert(log_files_id, "end", text="📂 Open EVTX / EVT File...", values=("open_file", "action", ""))

        # 4. Reusable Tasks (Matches Screenshot 1)
        self.tree.insert("", "end", text="📋 Audit logons", values=("audit_logons", "task", ""))
        self.tree.insert("", "end", text="📋 Admin Events", values=("admin_events", "task", ""))
        self.tree.insert("", "end", text="🖴 PC_DRIVE_E", values=("drive_e", "action", ""))

        # 5. Task Templates (Matches Screenshot 2!)
        templates_root = self.tree.insert("", "end", text="📁 Task templates", open=True)
        
        # Subfolders
        admin_folder = self.tree.insert(templates_root, "end", text="📁 Administrative", open=False)
        app_folder = self.tree.insert(templates_root, "end", text="📁 Application", open=False)
        audit_folder = self.tree.insert(templates_root, "end", text="📁 Audit", open=True)
        net_folder = self.tree.insert(templates_root, "end", text="📁 Network", open=False)
        sys_folder = self.tree.insert(templates_root, "end", text="📁 System", open=True)

        # Audit Tasks from templates
        self.tree.insert(audit_folder, "end", text="📁 Task Scheduler", open=False)
        self.tree.insert(audit_folder, "end", text="📁 Windows Firewall", open=False)

        for tmpl in TASK_TEMPLATES:
            target_parent = audit_folder if tmpl.category == "Audit" else sys_folder
            self.tree.insert(target_parent, "end", text=f"📋 {tmpl.name}", values=(tmpl.template_id, "template", ""))

    def _filter_tree(self) -> None:
        q = self.search_var.get().strip().lower()
        if not q:
            self._populate_tree()
            return
            
        self.tree.delete(*self.tree.get_children())
        res_root = self.tree.insert("", "end", text=f"🔍 Search Results for '{q}'", open=True)
        
        # Match channels
        for ch in ChannelManager.get_all_channels():
            if q in ch.lower():
                self.tree.insert(res_root, "end", text=f"📄 {ch}", values=(ch, "channel", "LocalPC"))

        # Match templates
        for tmpl in TASK_TEMPLATES:
            if q in tmpl.name.lower() or q in tmpl.description.lower():
                self.tree.insert(res_root, "end", text=f"📋 {tmpl.name}", values=(tmpl.template_id, "template", ""))

    def _on_double_click(self, event) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if not vals:
            return

        val, kind, comp = vals[0], vals[1], vals[2] if len(vals) > 2 else ""

        if kind == "channel":
            self.on_channel_selected(val, True, comp)
        elif kind == "action" and val == "open_file":
            self.on_open_file_requested()
        elif kind == "template":
            # Find template
            for t in TASK_TEMPLATES:
                if t.template_id == val:
                    self.on_template_selected(t)
                    break
        elif kind == "task":
            # Quick task template
            for t in TASK_TEMPLATES:
                if val in t.template_id:
                    self.on_template_selected(t)
                    break

    def _on_right_click(self, event) -> None:
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            vals = self.tree.item(item, "values")
            if vals and vals[1] == "channel":
                self.context_menu.post(event.x_root, event.y_root)

    def _menu_open_new_tab(self) -> None:
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            if vals and vals[1] == "channel":
                self.on_channel_selected(vals[0], True, vals[2])

    def _menu_open_current_tab(self) -> None:
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            if vals and vals[1] == "channel":
                self.on_channel_selected(vals[0], False, vals[2])
