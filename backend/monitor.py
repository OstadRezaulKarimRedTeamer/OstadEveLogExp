"""
Event Log Explorer - Live Monitoring & Alerter
Background monitor for real-time Windows Event Log streaming.
"""

import threading
import time
from typing import Callable, Optional, List
import win32evtlog
from .models import EventRecord
from .log_reader import parse_event_xml


class LogMonitor(threading.Thread):
    """Watches a specific Windows Event Log channel for new events."""

    def __init__(
        self,
        channel: str,
        interval_sec: float = 3.0,
        on_new_events: Optional[Callable[[List[EventRecord]], None]] = None,
        on_alert: Optional[Callable[[EventRecord], None]] = None
    ):
        super().__init__(daemon=True)
        self.channel = channel
        self.interval_sec = interval_sec
        self.on_new_events = on_new_events
        self.on_alert = on_alert
        self.running = False
        self._stop_event = threading.Event()
        self.last_record_id: Optional[int] = None

    def run(self) -> None:
        self.running = True
        
        # Initial query to determine latest record ID
        try:
            flags = win32evtlog.EvtQueryChannelPath | win32evtlog.EvtQueryReverseDirection
            qh = win32evtlog.EvtQuery(self.channel, flags, "*")
            initial_events = win32evtlog.EvtNext(qh, 1)
            if initial_events:
                xml_str = win32evtlog.EvtRender(initial_events[0], win32evtlog.EvtRenderEventXml)
                rec = parse_event_xml(xml_str, channel_fallback=self.channel)
                self.last_record_id = rec.record_id
        except Exception:
            pass

        while not self._stop_event.is_set():
            time.sleep(self.interval_sec)
            if self._stop_event.is_set():
                break

            try:
                # Query newest events
                flags = win32evtlog.EvtQueryChannelPath | win32evtlog.EvtQueryReverseDirection
                qh = win32evtlog.EvtQuery(self.channel, flags, "*")
                new_raw = win32evtlog.EvtNext(qh, 20)
                if not new_raw:
                    continue

                new_records: List[EventRecord] = []
                for h in new_raw:
                    xml_str = win32evtlog.EvtRender(h, win32evtlog.EvtRenderEventXml)
                    rec = parse_event_xml(xml_str, channel_fallback=self.channel, handle=h)
                    
                    if self.last_record_id is not None and rec.record_id <= self.last_record_id:
                        break
                    new_records.append(rec)

                if new_records:
                    self.last_record_id = new_records[0].record_id
                    if self.on_new_events:
                        self.on_new_events(new_records)
                        
                    # Check for alerts (Error / Critical)
                    if self.on_alert:
                        for r in new_records:
                            if r.level_name in ("Critical", "Error", "Audit Failure"):
                                self.on_alert(r)
            except Exception:
                pass

        self.running = False

    def stop(self) -> None:
        self._stop_event.set()
