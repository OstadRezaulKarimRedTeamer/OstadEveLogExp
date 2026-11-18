"""
Event Log Explorer - Color Coding Engine
Evaluates color coding rules and applies background/foreground styling.
"""

import json
import os
from typing import List, Optional, Tuple
from .models import EventRecord, ColorRule

DEFAULT_COLOR_RULES: List[ColorRule] = [
    ColorRule(
        rule_id="default_critical",
        name="Critical Events",
        enabled=True,
        match_field="Level",
        match_op="equals",
        match_val="Critical",
        bg_color="#7F0000",
        fg_color="#FFFFFF",
        priority=100
    ),
    ColorRule(
        rule_id="default_error",
        name="Error Events",
        enabled=True,
        match_field="Level",
        match_op="equals",
        match_val="Error",
        bg_color="#FFD6D6",
        fg_color="#900C3F",
        priority=90
    ),
    ColorRule(
        rule_id="default_audit_failure",
        name="Audit Failure (Logon Failures / Security)",
        enabled=True,
        match_field="Level",
        match_op="equals",
        match_val="Audit Failure",
        bg_color="#FFE0E6",
        fg_color="#C70039",
        priority=85
    ),
    ColorRule(
        rule_id="default_warning",
        name="Warning Events",
        enabled=True,
        match_field="Level",
        match_op="equals",
        match_val="Warning",
        bg_color="#FFF3CD",
        fg_color="#856404",
        priority=80
    ),
    ColorRule(
        rule_id="default_audit_success",
        name="Audit Success",
        enabled=True,
        match_field="Level",
        match_op="equals",
        match_val="Audit Success",
        bg_color="#E8F8F5",
        fg_color="#117A65",
        priority=70
    ),
    ColorRule(
        rule_id="default_failed_logon_id",
        name="Security: Failed Logon (Event ID 4625)",
        enabled=True,
        match_field="EventID",
        match_op="equals",
        match_val="4625",
        bg_color="#FADBD8",
        fg_color="#78281F",
        priority=95
    ),
]


class ColorEngine:
    """Manages color rules and computes row styles for event records."""
    
    def __init__(self, rules_file: Optional[str] = None):
        self.rules_file = rules_file or os.path.join(os.path.dirname(__file__), "..", "color_rules.json")
        self.rules: List[ColorRule] = []
        self.load_rules()

    def load_rules(self) -> None:
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.rules = [ColorRule(**item) for item in data]
                return
            except Exception:
                pass
        self.rules = list(DEFAULT_COLOR_RULES)

    def save_rules(self) -> None:
        try:
            data = [r.__dict__ for r in self.rules]
            with open(self.rules_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_color_for_record(self, record: EventRecord) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns (bg_color, fg_color) for the first matching enabled rule,
        ordered by priority descending.
        """
        sorted_rules = sorted([r for r in self.rules if r.enabled], key=lambda x: x.priority, reverse=True)
        
        for rule in sorted_rules:
            matched = False
            val_to_check = ""
            
            if rule.match_field == "Level":
                val_to_check = record.level_name
            elif rule.match_field == "EventID":
                val_to_check = str(record.event_id)
            elif rule.match_field == "Source":
                val_to_check = record.provider_name
            elif rule.match_field == "User":
                val_to_check = record.user_name
            elif rule.match_field == "Text":
                val_to_check = record.description
                
            if rule.match_op == "equals":
                matched = val_to_check.strip().lower() == rule.match_val.strip().lower()
            elif rule.match_op == "contains":
                matched = rule.match_val.strip().lower() in val_to_check.strip().lower()
            elif rule.match_op == "in_list":
                items = [x.strip().lower() for x in rule.match_val.split(",") if x.strip()]
                matched = val_to_check.strip().lower() in items

            if matched:
                return rule.bg_color, rule.fg_color

        return None, None
