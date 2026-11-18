"""
Event Log Explorer - Built-in AI Copilot / Incident Analyst Window
Triggered by the AI toolbar button matching the 2026 Event Log Explorer feature.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import urllib.parse
from typing import Optional
from backend.models import EventRecord


class AICopilotDialog(tk.Toplevel):
    """Analyst-controlled AI Copilot dialog."""

    def __init__(self, parent: tk.Widget, record: Optional[EventRecord]):
        super().__init__(parent)
        self.title("AI Assistant / Copilot - Event Log Explorer")
        self.geometry("640x520")
        self.transient(parent)

        self.record = record
        self._build_ui()

    def _build_ui(self) -> None:
        f = ttk.Frame(self, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="🤖 Analyst-Controlled AI Assistant", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(
            f,
            text="Inspect event forensics, generate threat hypotheses, or explain cryptic Windows event codes:",
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(0, 8))

        # Event Preview Strip
        ev_summary = f"Event ID: {self.record.event_id if self.record else 'None'} | Source: {self.record.provider_name if self.record else 'None'} | Level: {self.record.level_name if self.record else 'None'}"
        lbl_info = ttk.Label(f, text=ev_summary, font=("Segoe UI", 9, "bold"), foreground="#005A9E")
        lbl_info.pack(anchor=tk.W, pady=(0, 6))

        # Prompt Text
        ttk.Label(f, text="Generated Analysis Prompt:").pack(anchor=tk.W, pady=(0, 2))
        self.txt_prompt = tk.Text(f, height=12, wrap=tk.WORD, font=("Consolas", 9), relief=tk.SOLID, borderwidth=1, padx=8, pady=8)
        self.txt_prompt.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        if self.record:
            sample_prompt = f"""Explain Windows Event ID {self.record.event_id} from provider '{self.record.provider_name}'.
Time: {self.record.time_created_str}
Channel: {self.record.channel}
User: {self.record.user_name}
Computer: {self.record.computer}
Details:
{self.record.description}

1. What is the standard security or administrative significance of this event?
2. Does this indicate malicious activity, a system misconfiguration, or normal operation?
3. What are the recommended incident response triage steps?
"""
            self.txt_prompt.insert("1.0", sample_prompt)

        # Bottom buttons
        btn_bar = ttk.Frame(f)
        btn_bar.pack(fill=tk.X, pady=(4, 0))

        ttk.Button(btn_bar, text="📋 Copy Prompt", command=self._copy_prompt).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="🌐 Ask in Browser (Google / AI)", command=self._ask_online).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_bar, text="Close", command=self.destroy).pack(side=tk.RIGHT)

    def _copy_prompt(self) -> None:
        p = self.txt_prompt.get("1.0", tk.END).strip()
        if p:
            self.clipboard_clear()
            self.clipboard_append(p)
            messagebox.showinfo("Copied", "Prompt copied to clipboard!", parent=self)

    def _ask_online(self) -> None:
        p = self.txt_prompt.get("1.0", tk.END).strip()
        if self.record:
            q = urllib.parse.quote(f"Windows Event ID {self.record.event_id} {self.record.provider_name} explanation triage")
            webbrowser.open(f"https://www.google.com/search?q={q}")
