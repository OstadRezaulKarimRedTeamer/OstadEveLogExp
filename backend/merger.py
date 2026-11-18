"""
Event Log Explorer - Log Merger Engine
Merges events from multiple channels and EVTX files into one chronological view.
"""

from typing import List, Callable, Optional
from datetime import datetime
from .models import EventRecord
from .log_reader import LogReader


class LogMerger:
    """Merges and chronologically sorts events from multiple sources."""

    @staticmethod
    def merge_sources(
        sources: List[dict], # [{"path": "System", "is_file": False, "computer": "SRV002"}, ...]
        max_events_per_source: int = 2500,
        reverse: bool = True,
        on_progress: Optional[Callable[[str], None]] = None
    ) -> List[EventRecord]:
        merged: List[EventRecord] = []

        for idx, src in enumerate(sources):
            path = src["path"]
            is_file = src.get("is_file", False)
            comp_override = src.get("computer")

            if on_progress:
                on_progress(f"Reading source ({idx+1}/{len(sources)}): {path}...")

            try:
                events = LogReader.read_events(
                    source_path=path,
                    is_file=is_file,
                    max_events=max_events_per_source,
                    reverse=False
                )
                if comp_override:
                    for ev in events:
                        ev.computer = comp_override
                merged.extend(events)
            except Exception:
                continue

        # Sort all events chronologically
        merged.sort(key=lambda r: r.time_created or datetime.min, reverse=reverse)
        return merged
