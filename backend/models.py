"""
Event Log Explorer - Data Models
Defines EventRecord, FilterCriteria, ColorRule, and TaskTemplate data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class EventRecord:
    record_id: int
    channel: str
    event_id: int
    level: int  # 1=Critical, 2=Error, 3=Warning, 4=Info, 0=Info, 5=Verbose
    level_name: str
    provider_name: str
    provider_guid: str
    time_created: Optional[datetime]
    date_str: str          # e.g. "16.09.2026"
    time_str: str          # e.g. "07:21:42"
    time_created_str: str  # e.g. "16.09.2026 07:21:42"
    task_category: str
    task_id: int
    keywords: str
    user_id: str
    user_name: str
    computer: str
    opcode: str
    version: int
    description: str
    xml_raw: str
    event_data: Dict[str, Any] = field(default_factory=dict)
    bookmarked: bool = False
    notes: str = ""
    color_tag: str = ""
    handle: Any = None

    def matches_search(self, term: str) -> bool:
        """Case-insensitive substring search across common fields."""
        term = term.lower()
        if term in str(self.event_id):
            return True
        if term in self.provider_name.lower():
            return True
        if term in self.level_name.lower():
            return True
        if term in self.user_name.lower() or term in self.user_id.lower():
            return True
        if term in self.computer.lower():
            return True
        if term in self.channel.lower():
            return True
        if term in self.task_category.lower():
            return True
        if term in self.description.lower():
            return True
        for k, v in self.event_data.items():
            if term in str(k).lower() or term in str(v).lower():
                return True
        return False


@dataclass
class FilterCriteria:
    levels: List[str] = field(default_factory=lambda: ["Critical", "Error", "Warning", "Information", "Audit Success", "Audit Failure", "Verbose"])
    event_ids_include: List[int] = field(default_factory=list)
    event_ids_exclude: List[int] = field(default_factory=list)
    sources_include: List[str] = field(default_factory=list)
    users_include: List[str] = field(default_factory=list)
    search_text: str = ""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    def is_active(self) -> bool:
        if len(self.levels) < 7:
            return True
        if self.event_ids_include or self.event_ids_exclude:
            return True
        if self.sources_include or self.users_include:
            return True
        if self.search_text.strip():
            return True
        if self.date_from is not None or self.date_to is not None:
            return True
        return False


@dataclass
class ColorRule:
    rule_id: str
    name: str
    enabled: bool = True
    match_field: str = "Level"  # "Level", "EventID", "Source", "User", "Text"
    match_op: str = "equals"    # "equals", "contains", "in_list"
    match_val: str = "Error"
    bg_color: str = "#FFECEC"
    fg_color: str = "#B71C1C"
    priority: int = 0


@dataclass
class TaskTemplate:
    template_id: str
    category: str              # e.g. "Audit", "System", "Application"
    name: str                  # e.g. "Audit RDP logons"
    description: str
    target_channel: str        # e.g. "Security", "System"
    event_ids: List[int]       # e.g. [4624, 4625]
    levels: List[str]          # e.g. ["Audit Success", "Audit Failure"]
    sources: List[str] = field(default_factory=list)
    xml_query: str = ""
