"""
Event Log Explorer - Details Pane (Lower Pane matching Screenshot 1)
Features:
- Header bar: "Description" with 'X' close button
- Main content area
- Bottom tabs: "Description" and "Data"
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from backend.models import EventRecord
from backend.log_reader import format_event_description


class DetailsPane(ttk.Frame):
    """Lower split pane showing event description and raw data matching Event Log Explorer."""

    def __init__(self, parent: tk.Widget, on_close: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.on_close = on_close
        self.current_record: Optional[EventRecord] = None

        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Header Bar ("Description" with 'X' close button on right)
        header_bar = tk.Frame(self, bg="#F0F0F0", relief=tk.FLAT, height=24)
        header_bar.pack(fill=tk.X, side=tk.TOP, padx=2, pady=(1, 2))

        lbl_title = tk.Label(
            header_bar,
            text="Description",
            bg="#F0F0F0",
            fg="#000000",
            font=("Segoe UI", 9, "bold")
        )
        lbl_title.pack(side=tk.LEFT, padx=6)

        btn_close = tk.Button(
            header_bar,
            text="✕",
            font=("Segoe UI", 8),
            bg="#F0F0F0",
            relief=tk.FLAT,
            bd=0,
            padx=6,
            command=self._handle_close
        )
        btn_close.pack(side=tk.RIGHT, padx=2)

        # 2. Main Tabbed Container with tabs on the BOTTOM
        # To get tabs on the bottom in Tkinter, style notebook with tabposition='sw'
        style = ttk.Style(self)
        style.configure("Bottom.TNotebook", tabposition="sw")

        self.notebook = ttk.Notebook(self, style="Bottom.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Tab 1: Description
        self.tab_desc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_desc, text=" Description ")
        self._build_desc_tab()

        # Tab 2: Data (Event Data & Binary Dump)
        self.tab_data = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_data, text=" Data ")
        self._build_data_tab()

    def _build_desc_tab(self) -> None:
        f = ttk.Frame(self.tab_desc)
        f.pack(fill=tk.BOTH, expand=True)

        self.txt_desc = tk.Text(
            f,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=8
        )
        vsb = ttk.Scrollbar(f, orient="vertical", command=self.txt_desc.yview)
        self.txt_desc.configure(yscrollcommand=vsb.set)

        self.txt_desc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_data_tab(self) -> None:
        f = ttk.Frame(self.tab_data)
        f.pack(fill=tk.BOTH, expand=True)

        # Split into Key-Value Tree and Raw XML/Hex
        cols = ("Parameter", "Value")
        self.data_tree = ttk.Treeview(f, columns=cols, show="headings", selectmode="browse")
        self.data_tree.heading("Parameter", text="Parameter Name")
        self.data_tree.heading("Value", text="Value")
        self.data_tree.column("Parameter", width=220, anchor=tk.W)
        self.data_tree.column("Value", width=600, anchor=tk.W)

        d_vsb = ttk.Scrollbar(f, orient="vertical", command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=d_vsb.set)

        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        d_vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def display_record(self, record: Optional[EventRecord]) -> None:
        self.current_record = record
        if not record:
            self.txt_desc.delete("1.0", tk.END)
            self.data_tree.delete(*self.data_tree.get_children())
            return

        # Format full message description
        full_msg = format_event_description(record.provider_name, record.handle, record.event_data)
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", full_msg)

        # Update Data Tab
        self.data_tree.delete(*self.data_tree.get_children())
        if record.event_data:
            for k, v in record.event_data.items():
                self.data_tree.insert("", "end", values=(k, str(v)))
        else:
            self.data_tree.insert("", "end", values=("<No EventData>", "Event does not contain binary/custom parameters"))

    def _handle_close(self) -> None:
        if self.on_close:
            self.on_close()
