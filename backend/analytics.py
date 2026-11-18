"""
Event Log Explorer - Analytics & Statistics Module
Aggregates and computes statistical summaries for event logs.
"""

from collections import Counter
from typing import List, Dict, Any
from .models import EventRecord

# Common well-known Windows Event IDs for automatic annotation
KNOWN_EVENT_IDS = {
    # Security Log
    4624: "Successful Account Logon",
    4625: "Failed Account Logon Attempt",
    4634: "An account was logged off",
    4648: "A logon was attempted using explicit credentials",
    4672: "Special privileges assigned to new logon",
    4688: "A new process has been created",
    4689: "A process has exited",
    4720: "A user account was created",
    4722: "A user account was enabled",
    4724: "An attempt was made to reset an account's password",
    4728: "A member was added to a security-enabled global group",
    4738: "A user account was modified",
    1102: "The audit log was cleared",
    # System Log
    1074: "System shutdown/restart initiated",
    6005: "The Event log service was started (Boot)",
    6006: "The Event log service was stopped (Shutdown)",
    6008: "The previous system shutdown was unexpected",
    7036: "Service entered a running/stopped state",
    7040: "Service start type was changed",
    10016: "DCOM permissions issue",
    41: "Kernel-Power: System rebooted without cleanly shutting down",
    # Application / Windows Update
    1000: "Application Error / Crash",
    1001: "Windows Error Reporting (WER)",
    1002: "Application Hang",
    19: "Windows Update installation successfully scheduled",
    43: "Windows Update installation started",
    44: "Windows Update installation completed",
}


class LogAnalytics:
    """Computes distribution statistics, rankings, and incident triage data."""

    @staticmethod
    def generate_summary(records: List[EventRecord]) -> Dict[str, Any]:
        total = len(records)
        if total == 0:
            return {
                "total": 0,
                "levels": {},
                "top_event_ids": [],
                "top_sources": [],
                "top_users": [],
                "top_computers": []
            }

        level_counter = Counter(r.level_name for r in records)
        id_counter = Counter(r.event_id for r in records)
        source_counter = Counter(r.provider_name for r in records if r.provider_name)
        user_counter = Counter(r.user_name for r in records if r.user_name and r.user_name != "N/A")
        computer_counter = Counter(r.computer for r in records if r.computer)

        top_event_ids = []
        for ev_id, cnt in id_counter.most_common(15):
            pct = round((cnt / total) * 100, 1)
            desc = KNOWN_EVENT_IDS.get(ev_id, "Standard Event")
            top_event_ids.append({
                "event_id": ev_id,
                "count": cnt,
                "percentage": pct,
                "description": desc
            })

        top_sources = [
            {"source": src, "count": cnt, "percentage": round((cnt / total) * 100, 1)}
            for src, cnt in source_counter.most_common(10)
        ]

        top_users = [
            {"user": usr, "count": cnt, "percentage": round((cnt / total) * 100, 1)}
            for usr, cnt in user_counter.most_common(10)
        ]

        top_computers = [
            {"computer": comp, "count": cnt}
            for comp, cnt in computer_counter.most_common(5)
        ]

        return {
            "total": total,
            "levels": dict(level_counter),
            "top_event_ids": top_event_ids,
            "top_sources": top_sources,
            "top_users": top_users,
            "top_computers": top_computers
        }
