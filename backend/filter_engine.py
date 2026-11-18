"""
Event Log Explorer - Filter Engine
Provides flexible, fast filtering capabilities matching Event Log Explorer.
"""

from typing import List, Set, Optional
from datetime import datetime
from .models import EventRecord, FilterCriteria


def parse_id_ranges(id_string: str) -> Set[int]:
    """Parse comma/space separated IDs and ranges, e.g. '4624, 4625, 7000-7050'."""
    ids = set()
    if not id_string:
        return ids
    
    parts = id_string.replace(";", ",").replace(" ", ",").split(",")
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if "-" in p:
            try:
                start_s, end_s = p.split("-", 1)
                start, end = int(start_s.strip()), int(end_s.strip())
                if start <= end and (end - start) < 50000:
                    for i in range(start, end + 1):
                        ids.add(i)
            except ValueError:
                pass
        else:
            try:
                ids.add(int(p))
            except ValueError:
                pass
    return ids


class FilterEngine:
    """Evaluates filter criteria against EventRecord objects."""
    
    @staticmethod
    def evaluate(record: EventRecord, criteria: FilterCriteria) -> bool:
        # 1. Level filter
        if criteria.levels and record.level_name not in criteria.levels:
            return False
            
        # 2. Event ID Include
        if criteria.event_ids_include:
            if record.event_id not in criteria.event_ids_include:
                return False
                
        # 3. Event ID Exclude
        if criteria.event_ids_exclude:
            if record.event_id in criteria.event_ids_exclude:
                return False
                
        # 4. Sources Include
        if criteria.sources_include:
            matched_src = any(s.lower() in record.provider_name.lower() for s in criteria.sources_include)
            if not matched_src:
                return False
                
        # 5. Users Include
        if criteria.users_include:
            matched_user = any(
                u.lower() in record.user_name.lower() or u.lower() in record.user_id.lower()
                for u in criteria.users_include
            )
            if not matched_user:
                return False
                
        # 6. Date Range
        if criteria.date_from and record.time_created:
            # Ensure timezone awareness matches
            if record.time_created.tzinfo and not criteria.date_from.tzinfo:
                dt_from = criteria.date_from.astimezone()
            else:
                dt_from = criteria.date_from
            if record.time_created < dt_from:
                return False
                
        if criteria.date_to and record.time_created:
            if record.time_created.tzinfo and not criteria.date_to.tzinfo:
                dt_to = criteria.date_to.astimezone()
            else:
                dt_to = criteria.date_to
            if record.time_created > dt_to:
                return False
                
        # 7. Search Text
        if criteria.search_text.strip():
            if not record.matches_search(criteria.search_text.strip()):
                return False
                
        return True

    @classmethod
    def filter_records(cls, records: List[EventRecord], criteria: FilterCriteria) -> List[EventRecord]:
        if not criteria.is_active():
            return records
        return [r for r in records if cls.evaluate(r, criteria)]
