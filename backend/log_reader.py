"""
Event Log Explorer - Log Reader Engine
Handles Windows Event Log reading from live channels and .evtx files.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Optional, Callable, Dict, Any
import win32evtlog
from .models import EventRecord
from .sid_resolver import resolve_sid

_METADATA_CACHE: Dict[str, Any] = {}
_NS = {"ns": "http://schemas.microsoft.com/win/2004/08/events/event"}


def _get_level_name(level_val: int, keywords_hex: str, channel: str) -> str:
    """Map numeric level and keywords to standard Event Log Explorer level name."""
    try:
        kw = int(keywords_hex, 16) if keywords_hex.startswith("0x") else int(keywords_hex)
    except Exception:
        kw = 0

    if channel and "security" in channel.lower():
        if kw & 0x0020000000000000 or kw & 0x8020000000000000:
            return "Audit Success"
        if kw & 0x0010000000000000 or kw & 0x8010000000000000:
            return "Audit Failure"

    if level_val == 1:
        return "Critical"
    elif level_val == 2:
        return "Error"
    elif level_val == 3:
        return "Warning"
    elif level_val == 4 or level_val == 0:
        return "Information"
    elif level_val == 5:
        return "Verbose"
    return "Information"


def format_event_description(provider_name: str, event_handle: Any, fallback_data: Dict[str, Any]) -> str:
    """Format full human-readable event message using provider metadata."""
    if not provider_name or not event_handle:
        return _format_fallback_description(fallback_data)
    
    try:
        if provider_name not in _METADATA_CACHE:
            try:
                _METADATA_CACHE[provider_name] = win32evtlog.EvtOpenPublisherMetadata(provider_name)
            except Exception:
                _METADATA_CACHE[provider_name] = None
        
        meta = _METADATA_CACHE[provider_name]
        if meta:
            msg = win32evtlog.EvtFormatMessage(meta, event_handle, win32evtlog.EvtFormatMessageEvent)
            if msg:
                return msg.strip()
    except Exception:
        pass

    return _format_fallback_description(fallback_data)


def _format_fallback_description(event_data: Dict[str, Any]) -> str:
    """Create a readable summary from EventData when publisher message is unavailable."""
    if not event_data:
        return "No description available for this event."
    lines = []
    for k, v in event_data.items():
        if v:
            lines.append(f"{k}: {v}")
    return "\n".join(lines) if lines else "Event recorded without message string."


def parse_event_xml(xml_str: str, channel_fallback: str = "", handle: Any = None) -> EventRecord:
    """Parse raw Windows Event XML into an EventRecord instance."""
    root = ET.fromstring(xml_str)
    
    # System node
    sys = root.find("ns:System", _NS)
    
    # Event ID
    ev_id_node = sys.find("ns:EventID", _NS) if sys is not None else None
    event_id = int(ev_id_node.text) if ev_id_node is not None and ev_id_node.text else 0
    
    # Version
    version_node = sys.find("ns:Version", _NS) if sys is not None else None
    version = int(version_node.text) if version_node is not None and version_node.text else 0
    
    # Level
    level_node = sys.find("ns:Level", _NS) if sys is not None else None
    level = int(level_node.text) if level_node is not None and level_node.text else 4
    
    # Task / Category
    task_node = sys.find("ns:Task", _NS) if sys is not None else None
    task_id = int(task_node.text) if task_node is not None and task_node.text else 0
    task_category = f"Task {task_id}" if task_id != 0 else "None"
    
    # Opcode
    opcode_node = sys.find("ns:Opcode", _NS) if sys is not None else None
    opcode = opcode_node.text if opcode_node is not None and opcode_node.text else "Info"
    
    # Keywords
    kw_node = sys.find("ns:Keywords", _NS) if sys is not None else None
    keywords = kw_node.text if kw_node is not None and kw_node.text else "0x0"
    
    # Provider
    prov_node = sys.find("ns:Provider", _NS) if sys is not None else None
    provider_name = prov_node.attrib.get("Name", "") if prov_node is not None else ""
    provider_guid = prov_node.attrib.get("Guid", "") if prov_node is not None else ""
    
    # TimeCreated (Format: Date "16.09.2026", Time "7:21:42")
    tc_node = sys.find("ns:TimeCreated", _NS) if sys is not None else None
    time_iso = tc_node.attrib.get("SystemTime", "") if tc_node is not None else ""
    time_created = None
    date_str = ""
    time_str = ""
    time_created_str = ""
    if time_iso:
        try:
            clean_iso = time_iso.split(".")[0] + "Z" if "." in time_iso else time_iso
            dt_utc = datetime.strptime(clean_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            dt_local = dt_utc.astimezone()
            time_created = dt_local
            date_str = dt_local.strftime("%d.%m.%Y")
            time_str = dt_local.strftime("%H:%M:%S")
            time_created_str = f"{date_str} {time_str}"
        except Exception:
            date_str = time_iso[:10]
            time_str = time_iso[11:19]
            time_created_str = f"{date_str} {time_str}"
    
    # EventRecordID
    rec_node = sys.find("ns:EventRecordID", _NS) if sys is not None else None
    record_id = int(rec_node.text) if rec_node is not None and rec_node.text else 0
    
    # Channel
    chan_node = sys.find("ns:Channel", _NS) if sys is not None else None
    channel = chan_node.text if chan_node is not None and chan_node.text else channel_fallback
    
    # Computer
    comp_node = sys.find("ns:Computer", _NS) if sys is not None else None
    computer = comp_node.text if comp_node is not None and comp_node.text else "Localhost"
    
    # Security UserID
    sec_node = sys.find("ns:Security", _NS) if sys is not None else None
    user_id = sec_node.attrib.get("UserID", "") if sec_node is not None else ""
    user_name = resolve_sid(user_id) if user_id else "\\SYSTEM"
    
    # Level Name
    level_name = _get_level_name(level, keywords, channel)
    
    # EventData / UserData
    event_data: Dict[str, Any] = {}
    ed_node = root.find("ns:EventData", _NS)
    if ed_node is not None:
        idx = 1
        for elem in ed_node:
            key = elem.attrib.get("Name", f"Param{idx}")
            event_data[key] = elem.text or ""
            idx += 1
    else:
        ud_node = root.find("ns:UserData", _NS)
        if ud_node is not None:
            for child in ud_node:
                for sub in child:
                    key = sub.tag.split("}")[-1]
                    event_data[key] = sub.text or ""

    # Generate quick summary / description preview
    preview_parts = [f"{v}" for k, v in list(event_data.items())[:3] if v]
    preview = " | ".join(preview_parts) if preview_parts else f"Event ID {event_id} from {provider_name}"
    
    return EventRecord(
        record_id=record_id,
        channel=channel,
        event_id=event_id,
        level=level,
        level_name=level_name,
        provider_name=provider_name,
        provider_guid=provider_guid,
        time_created=time_created,
        date_str=date_str,
        time_str=time_str,
        time_created_str=time_created_str,
        task_category=task_category,
        task_id=task_id,
        keywords=keywords,
        user_id=user_id,
        user_name=user_name,
        computer=computer,
        opcode=opcode,
        version=version,
        description=preview,
        xml_raw=xml_str,
        event_data=event_data,
        handle=handle
    )


class LogReader:
    """High-performance log reader supporting Channels and standalone EVTX files."""
    
    @staticmethod
    def read_events(
        source_path: str,
        is_file: bool = False,
        max_events: int = 5000,
        xpath_query: str = "*",
        reverse: bool = True,
        on_batch: Optional[Callable[[List[EventRecord]], None]] = None,
        batch_size: int = 500,
        stop_check: Optional[Callable[[], bool]] = None
    ) -> List[EventRecord]:
        flags = win32evtlog.EvtQueryFilePath if is_file else win32evtlog.EvtQueryChannelPath
        if reverse:
            flags |= win32evtlog.EvtQueryReverseDirection
            
        try:
            query_handle = win32evtlog.EvtQuery(source_path, flags, xpath_query)
        except Exception as e:
            raise RuntimeError(f"Failed to open log '{source_path}': {e}")
        
        all_records: List[EventRecord] = []
        batch: List[EventRecord] = []
        
        while len(all_records) < max_events:
            if stop_check and stop_check():
                break
                
            fetch_count = min(batch_size, max_events - len(all_records))
            try:
                raw_events = win32evtlog.EvtNext(query_handle, fetch_count)
            except Exception:
                break
                
            if not raw_events:
                break
                
            for h in raw_events:
                try:
                    xml_str = win32evtlog.EvtRender(h, win32evtlog.EvtRenderEventXml)
                    rec = parse_event_xml(xml_str, channel_fallback=source_path, handle=h)
                    all_records.append(rec)
                    batch.append(rec)
                except Exception:
                    continue
            
            if on_batch and batch:
                on_batch(batch)
                batch = []
                
        return all_records
