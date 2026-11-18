"""
Event Log Explorer - Forensic Deep Scan & Output Window
Matches the exact deep-scan output dialog shown in Screenshot 3.
"""

import tkinter as tk
from tkinter import ttk


class DeepScanOutputDialog(tk.Toplevel):
    """Forensic scan diagnostic log window matching Screenshot 3."""

    def __init__(self, parent: tk.Widget, target_file: str, log_messages: list):
        super().__init__(parent)
        self.title("Output")
        self.geometry("520x380")
        self.transient(parent)

        f = ttk.Frame(self, padding=10)
        f.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(f)
        header.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(header, text="🔍 Forensic issues in " + target_file, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        self.txt = tk.Text(
            f,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#FFFFFF",
            relief=tk.SOLID,
            borderwidth=1,
            padx=8,
            pady=8
        )
        vsb = ttk.Scrollbar(f, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=vsb.set)

        self.txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        for line in log_messages:
            self.txt.insert(tk.END, line + "\n")

        # Bottom buttons
        btn_bar = ttk.Frame(self, padding=8)
        btn_bar.pack(fill=tk.X)

        ttk.Button(btn_bar, text="Close", width=9, command=self.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_bar, text="Clear", width=9, command=lambda: self.txt.delete("1.0", tk.END)).pack(side=tk.RIGHT)
