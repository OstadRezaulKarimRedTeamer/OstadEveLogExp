"""
Event Log Explorer - Channel Manager
Discovers, categorizes, and organizes Windows Event Channels.
"""

from typing import List, Dict
import win32evtlog

# Standard core Windows channels
STANDARD_WINDOWS_LOGS = [
    "Application",
    "Security",
    "Setup",
    "System",
    "ForwardedEvents"
]

POPULAR_DIAGNOSTIC_CHANNELS = [
    "Microsoft-Windows-Sysmon/Operational",
    "Microsoft-Windows-PowerShell/Operational",
    "Windows PowerShell",
    "Microsoft-Windows-TaskScheduler/Operational",
    "Microsoft-Windows-Windows Defender/Operational",
    "Microsoft-Windows-TerminalServices-LocalSessionManager/Operational",
    "Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational",
    "Microsoft-Windows-CodeIntegrity/Operational",
    "Microsoft-Windows-User Profile Service/Operational",
    "Microsoft-Windows-DNS-Client/Operational",
    "Microsoft-Windows-WinINet/UsageLog"
]


class ChannelManager:
    """Discovers and caches available Windows Event channels."""
    
    _cached_channels: List[str] = []

    @classmethod
    def get_all_channels(cls, force_refresh: bool = False) -> List[str]:
        if cls._cached_channels and not force_refresh:
            return cls._cached_channels
        
        channels = []
        try:
            enum_handle = win32evtlog.EvtOpenChannelEnum()
            while True:
                try:
                    ch = win32evtlog.EvtNextChannelPath(enum_handle)
                    if not ch:
                        break
                    channels.append(ch)
                except Exception:
                    break
        except Exception:
            # Fallback if channel enum is restricted
            channels = list(STANDARD_WINDOWS_LOGS) + list(POPULAR_DIAGNOSTIC_CHANNELS)
            
        cls._cached_channels = sorted(list(set(channels)))
        return cls._cached_channels

    @classmethod
    def get_categorized_channels(cls) -> Dict[str, List[str]]:
        all_ch = cls.get_all_channels()
        all_set = set(all_ch)
        
        std_logs = [c for c in STANDARD_WINDOWS_LOGS if c in all_set]
        popular_logs = [c for c in POPULAR_DIAGNOSTIC_CHANNELS if c in all_set]
        
        other_logs = [c for c in all_ch if c not in std_logs and c not in popular_logs]
        
        return {
            "Windows Logs": std_logs,
            "Popular Diagnostic Logs": popular_logs,
            "Applications and Services Logs": other_logs
        }
