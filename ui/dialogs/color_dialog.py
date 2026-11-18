"""
Event Log Explorer - Color Coding Rules Dialog
Allows configuring background/foreground color rules for rows matching Event Log Explorer.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import Callable, List, Optional
from backend.models import ColorRule
from backend.color_engine import ColorEngine, DEFAULT_COLOR_RULES


class ColorDialog(tk.Toplevel):
    """Configuration dialog for Event Log Color Coding rules."""

    def __init__(self, parent: tk.Widget, color_engine: ColorEngine, on_save: Callable[[], None]):
        super().__init__(parent)
        self.title("Color Coding Scheme - Event Log Explorer")
        self.geometry("640x540")
        self.transient(parent)
        self.grab_set()

        self.color_engine = color_engine
        self.on_save = on_save
        self.rules: List[ColorRule] = [ColorRule(**r.__dict__) for r in color_engine.rules]

        self._build_ui()
        self._populate_list()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main_frame,
            text="Define color rules to highlight specific events, error levels, or security incidents:",
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(0, 6))

        # Rules Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        cols = ("Enabled", "Name", "Field", "Condition", "Value", "Sample")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("Enabled", text="Active")
        self.tree.heading("Name", text="Rule Name")
        self.tree.heading("Field", text="Target Field")
        self.tree.heading("Condition", text="Operator")
        self.tree.heading("Value", text="Match Value")
        self.tree.heading("Sample", text="Color Preview")

        self.tree.column("Enabled", width=55, anchor=tk.CENTER)
        self.tree.column("Name", width=140, anchor=tk.W)
        self.tree.column("Field", width=80, anchor=tk.W)
        self.tree.column("Condition", width=80, anchor=tk.W)
        self.tree.column("Value", width=110, anchor=tk.W)
        self.tree.column("Sample", width=110, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Action Buttons for Rules
        btn_rule_bar = ttk.Frame(main_frame)
        btn_rule_bar.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(btn_rule_bar, text="➕ Add Rule", command=self._add_rule).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_rule_bar, text="✏️ Edit Rule", command=self._edit_rule).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_rule_bar, text="🗑️ Delete", command=self._delete_rule).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_rule_bar, text="Toggle Active", command=self._toggle_rule).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_rule_bar, text="↺ Defaults", command=self._reset_defaults).pack(side=tk.RIGHT)

        # Bottom OK / Cancel
        btn_box = ttk.Frame(main_frame)
        btn_box.pack(fill=tk.X, pady=(6, 0))

        ttk.Button(btn_box, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(btn_box, text="✔ Save & Apply", command=self._save_and_apply).pack(side=tk.RIGHT)

    def _populate_list(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx, r in enumerate(self.rules):
            active_str = "✔ Yes" if r.enabled else "No"
            sample_str = "Aa Sample Text"
            tag = f"tag_{r.rule_id}"
            
            self.tree.insert(
                "",
                "end",
                iid=str(idx),
                values=(active_str, r.name, r.match_field, r.match_op, r.match_val, sample_str),
                tags=(tag,)
            )
            self.tree.tag_configure(tag, background=r.bg_color, foreground=r.fg_color)

    def _on_select(self, event) -> None:
        pass

    def _toggle_rule(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        self.rules[idx].enabled = not self.rules[idx].enabled
        self._populate_list()
        self.tree.selection_set(str(idx))

    def _add_rule(self) -> None:
        self._rule_editor_popup(None)

    def _edit_rule(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Rule", "Please select a rule to edit.", parent=self)
            return
        idx = int(sel[0])
        self._rule_editor_popup(idx)

    def _delete_rule(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self.rules[idx]
        self._populate_list()

    def _reset_defaults(self) -> None:
        if messagebox.askyesno("Reset Rules", "Reset all color rules to factory defaults?", parent=self):
            self.rules = [ColorRule(**r.__dict__) for r in DEFAULT_COLOR_RULES]
            self._populate_list()

    def _save_and_apply(self) -> None:
        self.color_engine.rules = self.rules
        self.color_engine.save_rules()
        self.on_save()
        self.destroy()

    def _rule_editor_popup(self, edit_idx: Optional[int]) -> None:
        is_edit = edit_idx is not None
        rule = self.rules[edit_idx] if is_edit else ColorRule(
            rule_id=f"rule_{len(self.rules) + 1}",
            name="New Rule",
            enabled=True,
            match_field="Level",
            match_op="equals",
            match_val="Error",
            bg_color="#FFECEC",
            fg_color="#B71C1C",
            priority=50
        )

        win = tk.Toplevel(self)
        win.title("Edit Color Rule" if is_edit else "Add Color Rule")
        win.geometry("420x400")
        win.transient(self)
        win.grab_set()

        f = ttk.Frame(win, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Rule Name:").pack(anchor=tk.W)
        entry_name = ttk.Entry(f)
        entry_name.insert(0, rule.name)
        entry_name.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f, text="Target Field:").pack(anchor=tk.W)
        combo_field = ttk.Combobox(f, values=["Level", "EventID", "Source", "User", "Text"], state="readonly")
        combo_field.set(rule.match_field)
        combo_field.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f, text="Condition Operator:").pack(anchor=tk.W)
        combo_op = ttk.Combobox(f, values=["equals", "contains", "in_list"], state="readonly")
        combo_op.set(rule.match_op)
        combo_op.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f, text="Match Value:").pack(anchor=tk.W)
        entry_val = ttk.Entry(f)
        entry_val.insert(0, rule.match_val)
        entry_val.pack(fill=tk.X, pady=(0, 8))

        # Color Pickers
        bg_holder = [rule.bg_color]
        fg_holder = [rule.fg_color]

        color_frame = ttk.Frame(f)
        color_frame.pack(fill=tk.X, pady=6)

        lbl_preview = tk.Label(
            color_frame,
            text="Preview Text Sample",
            bg=bg_holder[0],
            fg=fg_holder[0],
            font=("Segoe UI", 10, "bold"),
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=4
        )
        lbl_preview.pack(fill=tk.X, pady=(0, 6))

        def pick_bg():
            c = colorchooser.askcolor(color=bg_holder[0], parent=win)[1]
            if c:
                bg_holder[0] = c
                lbl_preview.config(bg=c)

        def pick_fg():
            c = colorchooser.askcolor(color=fg_holder[0], parent=win)[1]
            if c:
                fg_holder[0] = c
                lbl_preview.config(fg=c)

        btn_c_frame = ttk.Frame(color_frame)
        btn_c_frame.pack(fill=tk.X)
        ttk.Button(btn_c_frame, text="🎨 Choose Background Color", command=pick_bg).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(btn_c_frame, text="✏️ Choose Text Color", command=pick_fg).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        def save_rule():
            name = entry_name.get().strip() or "Untitled"
            field = combo_field.get()
            op = combo_op.get()
            val = entry_val.get().strip()
            
            rule.name = name
            rule.match_field = field
            rule.match_op = op
            rule.match_val = val
            rule.bg_color = bg_holder[0]
            rule.fg_color = fg_holder[0]

            if not is_edit:
                self.rules.append(rule)
            self._populate_list()
            win.destroy()

        b_box = ttk.Frame(f)
        b_box.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(b_box, text="Cancel", command=win.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(b_box, text="Save Rule", command=save_rule).pack(side=tk.RIGHT)
