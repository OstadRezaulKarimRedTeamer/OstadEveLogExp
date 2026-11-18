"""
Event Log Explorer - Main Window (Exact replica of Screenshot 1, 2, and 3)
Forensic Edition matching https://eventlogxp.com/blog/windows-event-viewer-alternatives/
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import winsound
from typing import Dict, Optional, List
from backend.models import EventRecord, TaskTemplate
from backend.color_engine import ColorEngine
from backend.merger import LogMerger
from backend.templates import TASK_TEMPLATES
from ui.object_tree import ObjectTree
from ui.log_tab import LogTab
from ui.dialogs.color_dialog import ColorDialog
from ui.dialogs.stats_dialog import StatsDialog
from ui.dialogs.export_dialog import ExportDialog
from ui.dialogs.filter_dialog import FilterDialog
from ui.dialogs.task_template_dialog import CreateTaskFromTemplateDialog
from ui.dialogs.ai_copilot_dialog import AICopilotDialog
from ui.dialogs.deep_scan_dialog import DeepScanOutputDialog


class MainWindow(tk.Tk):
    """Ostad EveLogExp - Forensic Edition Main Window."""

    def __init__(self):
        super().__init__()
        # Title with custom branding
        self.title("Untitled.ELX - Ostad EveLogExp | Ostad Red Team Forge")
        self.geometry("1280x800")
        self.minsize(980, 620)

        # Set Application Branding Icon
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ico_file = os.path.join(base_dir, "assets", "app_icon.ico")
        png_file = os.path.join(base_dir, "assets", "app_icon.png")
        if os.path.exists(ico_file):
            try:
                self.iconbitmap(ico_file)
            except Exception:
                pass
        if os.path.exists(png_file):
            try:
                img_ico = tk.PhotoImage(file=png_file)
                self.iconphoto(False, img_ico)
            except Exception:
                pass

        # State
        self.color_engine = ColorEngine()
        self.tabs: Dict[str, LogTab] = {}
        self.bookmarked_records: List[EventRecord] = []
        self.current_workspace_name = "Untitled.ELX"

        # Setup styling
        self._setup_style()
        self._build_menu()
        self._build_toolbar()
        self._build_central_workspace()

        # Keyboard shortcuts
        self._bind_shortcuts()

        # Launch default tabs (Matches Screenshot 1: Admin Events, Merger)
        self.after(100, self._open_default_session)

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("vista" if "vista" in style.theme_names() else "clam")
        except Exception:
            pass

        # Windows classic tab styling
        style.configure("Treeview.Heading", font=("Segoe UI", 9), relief=tk.RAISED)
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=21)
        style.configure("TNotebook.Tab", font=("Segoe UI", 9), padding=[8, 3])

    def _build_menu(self) -> None:
        # Exact Menu Order from Screenshot 1:
        # File, Forensics, Database, Tree, Log, View, Event, Advanced, Script, Window, Help
        menubar = tk.Menu(self)

        # 1. File
        m_file = tk.Menu(menubar, tearoff=False)
        m_file.add_command(label="New Workspace", command=lambda: None)
        m_file.add_command(label="Open Workspace...", accelerator="Ctrl+O", command=lambda: None)
        m_file.add_command(label="Save Workspace", accelerator="Ctrl+S", command=lambda: None)
        m_file.add_command(label="Save Workspace As...", command=lambda: None)
        m_file.add_separator()
        m_file.add_command(label="Open Log File (EVTX / EVT)...", command=self.open_file_dialog)
        m_file.add_command(label="Export Log...", command=self.open_export_dialog)
        m_file.add_command(label="Print...", accelerator="Ctrl+P", command=self.open_export_dialog)
        m_file.add_separator()
        m_file.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_current_tab)
        m_file.add_command(label="Exit", accelerator="Alt+F4", command=self.quit)
        menubar.add_cascade(label="File", menu=m_file)

        # 2. Forensics (Forensic Edition feature from Screenshot 3!)
        m_forensics = tk.Menu(menubar, tearoff=False)
        m_forensics.add_command(label="Deep Scan Damaged EVTX / Raw Disk Image...", command=self.open_deep_scan_dialog)
        m_forensics.add_command(label="Search for Removed / Carved Events...", command=lambda: messagebox.showinfo("Forensics", "Carving unallocated EVTX record chunks..."))
        m_forensics.add_command(label="Snapshot Comparison...", command=lambda: None)
        m_forensics.add_separator()
        m_forensics.add_command(label="Analyze Memory / Raw VMDK Image...", command=self.open_deep_scan_dialog)
        menubar.add_cascade(label="Forensics", menu=m_forensics)

        # 3. Database
        m_db = tk.Menu(menubar, tearoff=False)
        m_db.add_command(label="Export Events to Database...", command=lambda: None)
        m_db.add_command(label="Central Collector Service (Elodea)...", command=lambda: None)
        menubar.add_cascade(label="Database", menu=m_db)

        # 4. Tree
        m_tree = tk.Menu(menubar, tearoff=False)
        m_tree.add_command(label="Add Computer...", command=self._prompt_add_computer)
        m_tree.add_command(label="Add Log File...", command=self.open_file_dialog)
        m_tree.add_command(label="Scan Network...", command=lambda: None)
        m_tree.add_separator()
        m_tree.add_command(label="Refresh Tree", command=lambda: self.object_tree._populate_tree())
        menubar.add_cascade(label="Tree", menu=m_tree)

        # 5. Log
        m_log = tk.Menu(menubar, tearoff=False)
        m_log.add_command(label="Filter...", accelerator="Ctrl+L", command=self.open_filter_dialog)
        m_log.add_command(label="Clear Filter", command=self.reset_active_filters)
        m_log.add_separator()
        m_log.add_command(label="Merge Logs...", command=self.open_merger_tab)
        m_log.add_command(label="Create Task from Template...", command=lambda: self._launch_template_wizard(TASK_TEMPLATES[0]))
        m_log.add_separator()
        m_log.add_command(label="Reload / Refresh", accelerator="F5", command=self.refresh_active_log)
        menubar.add_cascade(label="Log", menu=m_log)

        # 6. View
        m_view = tk.Menu(menubar, tearoff=False)
        m_view.add_command(label="Color Coding...", accelerator="Ctrl+K", command=self.open_color_dialog)
        m_view.add_command(label="Columns Setup...", command=lambda: None)
        m_view.add_separator()
        m_view.add_command(label="Toggle Objects Tree", accelerator="F4", command=self.toggle_sidebar)
        m_view.add_command(label="Toggle Description Pane", accelerator="F6", command=self.toggle_details_pane)
        menubar.add_cascade(label="View", menu=m_view)

        # 7. Event
        m_event = tk.Menu(menubar, tearoff=False)
        m_event.add_command(label="Event Properties", accelerator="Enter", command=self.open_active_properties)
        m_event.add_command(label="Copy Event Description", command=lambda: None)
        m_event.add_command(label="Bookmark Event", command=lambda: None)
        m_event.add_separator()
        m_event.add_command(label="Lookup Event ID Online", command=lambda: None)
        menubar.add_cascade(label="Event", menu=m_event)

        # 8. Advanced
        m_advanced = tk.Menu(menubar, tearoff=False)
        m_advanced.add_command(label="Analytical Summary & Statistics...", accelerator="Ctrl+T", command=self.open_stats_dialog)
        m_advanced.add_command(label="Pivot Table & Charts...", command=self.open_stats_dialog)
        m_advanced.add_separator()
        m_advanced.add_command(label="AI Copilot Assistant", command=self.open_ai_copilot)
        menubar.add_cascade(label="Advanced", menu=m_advanced)

        # 9. Script
        m_script = tk.Menu(menubar, tearoff=False)
        m_script.add_command(label="PascalScript Editor...", command=lambda: None)
        m_script.add_command(label="Run Automation Script...", command=lambda: None)
        menubar.add_cascade(label="Script", menu=m_script)

        # 10. Window
        m_window = tk.Menu(menubar, tearoff=False)
        m_window.add_command(label="Close Tab", command=self.close_current_tab)
        m_window.add_command(label="Close All Tabs", command=self.close_all_tabs)
        menubar.add_cascade(label="Window", menu=m_window)

        # 11. Help
        m_help = tk.Menu(menubar, tearoff=False)
        m_help.add_command(label="Ostad EveLogExp Help Topics", command=lambda: None)
        m_help.add_separator()
        m_help.add_command(label="About Ostad EveLogExp...", command=self._show_about)
        menubar.add_cascade(label="Help", menu=m_help)

        self.config(menu=menubar)

    def _build_toolbar(self) -> None:
        # Matches the exact toolbar from Screenshot 1 & 2:
        tb = tk.Frame(self, bg="#EAEAEA", height=32, relief=tk.RAISED, bd=1)
        tb.pack(fill=tk.X, side=tk.TOP, padx=1, pady=1)

        def make_btn(text: str, cmd, tip: str = ""):
            b = tk.Button(tb, text=text, font=("Segoe UI", 9), bg="#EAEAEA", relief=tk.FLAT, bd=0, padx=5, pady=2, command=cmd)
            b.pack(side=tk.LEFT, padx=1)
            return b

        # 1. Open Workspace
        make_btn("📁", lambda: None, "Open Workspace")
        # 2. Add Computer
        make_btn("🖥️➕", self._prompt_add_computer, "Add Computer")
        # 3. Add Log File
        make_btn("💾➕", self.open_file_dialog, "Add Log File")
        # 4. Open File (Blue folder)
        make_btn("📂", self.open_file_dialog, "Open Log File")
        # 5. Save Workspace
        make_btn("💾", lambda: None, "Save Workspace")
        # 6. Print / Export
        make_btn("🖶", self.open_export_dialog, "Print / Export")
        # 7. Refresh
        make_btn("🔄", self.refresh_active_log, "Refresh")

        # Separator
        tk.Label(tb, text="|", fg="#AAAAAA", bg="#EAEAEA").pack(side=tk.LEFT, padx=4)

        # Filter Dropdown: "<Load filter> ▼"
        self.combo_filter = ttk.Combobox(tb, values=["<Load filter>", "Audit RDP logons", "Audit failures", "Admin Events", "System Errors"], width=13, state="readonly")
        self.combo_filter.set("<Load filter>")
        self.combo_filter.pack(side=tk.LEFT, padx=2)
        self.combo_filter.bind("<<ComboboxSelected>>", self._on_filter_dropdown_selected)

        # Filter Icons (Blue funnel, Red funnel with X, Omega, Binoculars)
        make_btn("🔵", self.open_filter_dialog, "Apply Filter")
        make_btn("🔴", self.reset_active_filters, "Clear Filter")
        make_btn("🔬", self.open_filter_dialog, "Filter Builder")
        make_btn("🔦", self._find_in_table, "Find")

        # AI Copilot Button (Matches the blue AI badge in Screenshot 1 & 2!)
        btn_ai = tk.Button(
            tb,
            text="AI",
            font=("Segoe UI", 8, "bold"),
            bg="#0078D7",
            fg="#FFFFFF",
            relief=tk.FLAT,
            bd=0,
            padx=4,
            pady=1,
            command=self.open_ai_copilot
        )
        btn_ai.pack(side=tk.LEFT, padx=4)

        # Analytics / Report Button
        make_btn("📊", self.open_stats_dialog, "Analytics Summary")
        make_btn("🖨️", self.open_export_dialog, "Report")

        # Zoom / Size Slider on the Right (Matches Screenshot 1 slider!)
        lbl_excl = tk.Label(tb, text="!", font=("Segoe UI", 8, "bold"), fg="#555555", bg="#EAEAEA")
        lbl_excl.pack(side=tk.RIGHT, padx=4)

        slider = ttk.Scale(tb, from_=0, to=100, orient=tk.HORIZONTAL, length=80)
        slider.set(50)
        slider.pack(side=tk.RIGHT, padx=2)

    def _build_central_workspace(self) -> None:
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar (Objects Tree)
        self.sidebar_frame = ttk.Frame(self.main_paned, width=240)
        self.object_tree = ObjectTree(
            parent=self.sidebar_frame,
            on_channel_selected=self.open_channel,
            on_open_file_requested=self.open_file_dialog,
            on_template_selected=self._launch_template_wizard,
            on_close_sidebar=self.toggle_sidebar
        )
        self.object_tree.pack(fill=tk.BOTH, expand=True)
        self.main_paned.add(self.sidebar_frame, weight=1)

        # Right Tabbed Workspace
        self.notebook = ttk.Notebook(self.main_paned)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.main_paned.add(self.notebook, weight=4)

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.bind("<Control-s>", lambda e: self.open_export_dialog())
        self.bind("<Control-w>", lambda e: self.close_current_tab())
        self.bind("<F5>", lambda e: self.refresh_active_log())
        self.bind("<Control-k>", lambda e: self.open_color_dialog())
        self.bind("<Control-l>", lambda e: self.open_filter_dialog())
        self.bind("<Control-t>", lambda e: self.open_stats_dialog())
        self.bind("<F4>", lambda e: self.toggle_sidebar())
        self.bind("<F6>", lambda e: self.toggle_details_pane())

    def _open_default_session(self) -> None:
        """Launches the default tabs matching Screenshot 1 (Admin Events & Merger)."""
        # Tab 1: Admin Events
        self.open_channel("System", new_tab=True, computer="MIKE-LN", tab_title="📋 Admin Events")

        # Tab 2: Merger (The Multi-Channel & Multi-Computer view from Screenshot 1!)
        self.open_merger_tab()

    def open_channel(self, channel_name: str, new_tab: bool = True, computer: str = "", tab_title: str = "") -> None:
        comp = computer or os.environ.get("COMPUTERNAME", "LocalPC")
        tab_key = f"channel_{channel_name}_{comp}"
        
        if tab_key in self.tabs:
            self.notebook.select(self.tabs[tab_key])
            return

        tab = LogTab(
            parent=self.notebook,
            log_source=channel_name,
            is_file=False,
            color_engine=self.color_engine,
            computer_name=comp,
            on_open_analytics=self.open_stats_dialog
        )
        self.tabs[tab_key] = tab

        title_to_use = tab_title or f"📄 {channel_name}"
        self.notebook.add(tab, text=title_to_use)
        self.notebook.select(tab)

    def open_merger_tab(self) -> None:
        """Creates the 'Merger' tab (Screenshot 1: multiple channels & computers merged)."""
        tab_key = "tab_merger"
        if tab_key in self.tabs:
            self.notebook.select(self.tabs[tab_key])
            return

        # Matches Screenshot 1: "📁 Merger  x"
        tab = LogTab(
            parent=self.notebook,
            log_source="System",
            is_file=False,
            color_engine=self.color_engine,
            computer_name="SRV002",
            on_open_analytics=self.open_stats_dialog
        )

        # Merge System + Security + Application with simulated multi-machine attribution
        def merge_worker():
            try:
                sources = [
                    {"path": "System", "is_file": False, "computer": "SRV002"},
                    {"path": "System", "is_file": False, "computer": "MIKE-LN"},
                    {"path": "Security", "is_file": False, "computer": "VM11"}
                ]
                merged = LogMerger.merge_sources(sources, max_events_per_source=1500)
                self.after(0, lambda: self._apply_merged_records(tab, merged))
            except Exception:
                pass

        import threading
        threading.Thread(target=merge_worker, daemon=True).start()

        self.tabs[tab_key] = tab
        self.notebook.add(tab, text="📁 Merger  x")
        self.notebook.select(tab)

    def _apply_merged_records(self, tab: LogTab, records: List[EventRecord]) -> None:
        tab.all_records = records
        tab._refresh_table()

    def open_file_dialog(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Open Windows Event Log File",
            filetypes=[("Event Log Files (*.evtx;*.evt)", "*.evtx;*.evt"), ("All Files", "*.*")]
        )
        if not path:
            return

        filename = path.replace("\\", "/").split("/")[-1]
        tab_key = f"file_{path}"
        if tab_key in self.tabs:
            self.notebook.select(self.tabs[tab_key])
            return

        tab = LogTab(
            parent=self.notebook,
            log_source=path,
            is_file=True,
            color_engine=self.color_engine,
            computer_name="Localhost",
            on_open_analytics=self.open_stats_dialog
        )
        self.tabs[tab_key] = tab
        self.notebook.add(tab, text=f"📁 {filename}  x")
        self.notebook.select(tab)

    def _launch_template_wizard(self, template: TaskTemplate) -> None:
        """Opens Create Task from Template Wizard (Screenshot 2)."""
        CreateTaskFromTemplateDialog(self, template, self._on_template_finished)

    def _on_template_finished(self, template: TaskTemplate, task_name: str) -> None:
        # Open task tab and apply criteria
        tab_key = f"task_{template.template_id}"
        tab = LogTab(
            parent=self.notebook,
            log_source=template.target_channel or "Security",
            is_file=False,
            color_engine=self.color_engine,
            computer_name="LocalPC",
            on_open_analytics=self.open_stats_dialog
        )
        tab.criteria.event_ids_include = list(template.event_ids)
        self.tabs[tab_key] = tab
        self.notebook.add(tab, text=f"📋 {task_name}  x")
        self.notebook.select(tab)

    def open_deep_scan_dialog(self) -> None:
        """Forensic Deep Scan Output (Screenshot 3)."""
        sample_logs = [
            "Forensic issues in D:\\VM\\VMWARE\\Windows Server 2019\\Windows Server 2019-s001.vmdk",
            "Inconsistent data in a chunk ignored",
            "Inconsistent data in a chunk ignored",
            "Inconsistent data in a chunk ignored",
            "Inconsistent data in a chunk ignored",
            "Inconsistent data in a chunk ignored",
            "Inconsistent data in a chunk ignored",
            "Inconsistent data in a chunk ignored",
            "Inconsistent data in a chunk ignored",
            "Recovered intact event records: 25,231"
        ]
        DeepScanOutputDialog(self, "Windows Server 2019-s001.vmdk", sample_logs)

    def open_ai_copilot(self) -> None:
        """AI Assistant / Copilot (Triggered by AI button in toolbar)."""
        tab = self.get_active_tab()
        rec = tab.details_pane.current_record if tab else None
        AICopilotDialog(self, rec)

    def get_active_tab(self) -> Optional[LogTab]:
        selected = self.notebook.select()
        if not selected:
            return None
        for tab in self.tabs.values():
            if str(tab) == selected:
                return tab
        return None

    def close_current_tab(self) -> None:
        tab = self.get_active_tab()
        if not tab:
            return
        for k, v in list(self.tabs.items()):
            if v == tab:
                del self.tabs[k]
                break
        self.notebook.forget(tab)
        tab.destroy()

    def close_all_tabs(self) -> None:
        for tab in list(self.tabs.values()):
            self.notebook.forget(tab)
            tab.destroy()
        self.tabs.clear()

    def refresh_active_log(self) -> None:
        tab = self.get_active_tab()
        if tab:
            tab.load_log()

    def open_filter_dialog(self) -> None:
        tab = self.get_active_tab()
        if tab:
            sources = list(set(r.provider_name for r in tab.all_records if r.provider_name))
            FilterDialog(self, tab.criteria, sources, lambda c: self._apply_filter_to_active_tab(tab, c))

    def _apply_filter_to_active_tab(self, tab: LogTab, crit) -> None:
        tab.criteria = crit
        tab._refresh_table()

    def reset_active_filters(self) -> None:
        tab = self.get_active_tab()
        if tab:
            tab.criteria.event_ids_include = []
            tab.criteria.event_ids_exclude = []
            tab.criteria.sources_include = []
            tab.criteria.users_include = []
            tab.criteria.search_text = ""
            tab._refresh_table()

    def open_color_dialog(self) -> None:
        ColorDialog(self, self.color_engine, self._on_color_scheme_updated)

    def _on_color_scheme_updated(self) -> None:
        for tab in self.tabs.values():
            tab._refresh_table()

    def open_stats_dialog(self) -> None:
        tab = self.get_active_tab()
        if not tab or not tab.all_records:
            messagebox.showinfo("Analytics", "No records available to analyze.", parent=self)
            return
        StatsDialog(self, tab.filtered_records, title_prefix=tab.log_source)

    def open_export_dialog(self) -> None:
        tab = self.get_active_tab()
        if not tab or not tab.all_records:
            messagebox.showinfo("Export", "No log loaded to export.", parent=self)
            return
        ExportDialog(self, tab.all_records, tab.filtered_records, default_name=tab.log_source)

    def open_active_properties(self) -> None:
        tab = self.get_active_tab()
        if tab:
            tab._open_properties()

    def toggle_sidebar(self) -> None:
        if self.sidebar_frame.winfo_ismapped():
            self.main_paned.forget(self.sidebar_frame)
        else:
            self.main_paned.insert(0, self.sidebar_frame, weight=1)

    def toggle_details_pane(self) -> None:
        tab = self.get_active_tab()
        if tab:
            tab._toggle_details_pane()

    def _find_in_table(self) -> None:
        tab = self.get_active_tab()
        if not tab:
            return
        # Simple search dialog
        win = tk.Toplevel(self)
        win.title("Find in Log Events")
        win.geometry("340x120")
        win.transient(self)

        f = ttk.Frame(win, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Find text:").pack(anchor=tk.W)
        entry = ttk.Entry(f, width=32)
        entry.pack(fill=tk.X, pady=(2, 8))
        entry.focus_set()

        def do_find():
            txt = entry.get().strip().lower()
            if not txt:
                return
            for idx, r in enumerate(tab.filtered_records):
                if r.matches_search(txt):
                    tab.tree.selection_set(str(idx))
                    tab.tree.see(str(idx))
                    tab.details_pane.display_record(r)
                    win.destroy()
                    return
            messagebox.showinfo("Find", f"Pattern '{txt}' not found.", parent=win)

        ttk.Button(f, text="Find Next", command=do_find).pack(side=tk.RIGHT)
        ttk.Button(f, text="Cancel", command=win.destroy).pack(side=tk.RIGHT, padx=4)

    def _on_filter_dropdown_selected(self, event) -> None:
        val = self.combo_filter.get()
        tab = self.get_active_tab()
        if not tab:
            return
        if val == "Audit failures":
            tab.criteria.event_ids_include = [4625, 4776]
            tab._refresh_table()
        elif val == "Audit RDP logons":
            tab.criteria.event_ids_include = [4624, 4625, 1149]
            tab._refresh_table()
        elif val == "System Errors":
            tab.criteria.levels = ["Critical", "Error"]
            tab._refresh_table()

    def _prompt_add_computer(self) -> None:
        win = tk.Toplevel(self)
        win.title("Add Computer to Tree")
        win.geometry("360x140")
        win.transient(self)

        f = ttk.Frame(win, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Computer name or IP address:").pack(anchor=tk.W)
        entry = ttk.Entry(f, width=30)
        entry.insert(0, "SRV003")
        entry.pack(fill=tk.X, pady=(4, 10))

        def add_comp():
            c = entry.get().strip()
            if c:
                r_id = self.object_tree.tree.insert("", "end", text=f"🖥️ {c}", open=False)
                self.object_tree.tree.insert(r_id, "end", text="📄 System", values=("System", "channel", c))
                self.object_tree.tree.insert(r_id, "end", text="📄 Security", values=("Security", "channel", c))
                self.object_tree.tree.insert(r_id, "end", text="📄 Application", values=("Application", "channel", c))
            win.destroy()

        ttk.Button(f, text="Add", command=add_comp).pack(side=tk.RIGHT)
        ttk.Button(f, text="Cancel", command=win.destroy).pack(side=tk.RIGHT, padx=4)

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About Ostad EveLogExp",
            "Ostad EveLogExp - Enterprise Forensic & Threat Analysis Edition\n"
            "Official Tool of Ostad Red Team Forge\n\n"
            "★ Founder & Director: Ostad Rezaul Karim\n"
            "★ Profile: Top 1% Red Teamer • Cybersecurity Expert\n"
            "★ Expertise: Ethical Hacker • App Developer • Web Developer • IT Expert\n\n"
            "Key Features:\n"
            "• Multi-Channel & Multi-Computer Merger View\n"
            "• Reusable Investigation Tasks & Templates (Audit RDP, Logons, etc.)\n"
            "• Forensic Deep Scan of Damaged EVTX / Raw Disk Images\n"
            "• Analyst-controlled AI Copilot / Assistant\n"
            "• Custom Color Coding Schemes\n"
            "• Fast Export to HTML Web Report, CSV, JSON, XML",
            parent=self
        )
