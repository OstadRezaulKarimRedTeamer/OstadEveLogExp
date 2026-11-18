"""
Event Log Explorer - SID Resolver
Resolves Windows SIDs to human-readable usernames with thread-safe caching.
"""

import win32security

_SID_CACHE = {
    "S-1-5-18": "NT AUTHORITY\\SYSTEM",
    "S-1-5-19": "NT AUTHORITY\\LOCAL SERVICE",
    "S-1-5-20": "NT AUTHORITY\\NETWORK SERVICE",
    "S-1-5-32-544": "BUILTIN\\Administrators",
    "S-1-5-32-545": "BUILTIN\\Users",
}


def resolve_sid(sid_str: str) -> str:
    """Resolve a SID string (e.g., S-1-5-21-...) to Domain\\Username."""
    if not sid_str:
        return "N/A"
    
    if sid_str in _SID_CACHE:
        return _SID_CACHE[sid_str]
    
    try:
        sid_obj = win32security.GetBinarySid(sid_str)
        name, domain, _ = win32security.LookupAccountSid(None, sid_obj)
        if domain:
            readable = f"{domain}\\{name}"
        else:
            readable = name
        _SID_CACHE[sid_str] = readable
        return readable
    except Exception:
        # Fallback to truncated or original SID
        _SID_CACHE[sid_str] = sid_str
        return sid_str
