"""
Event Log Explorer - Investigation Task Templates
Matches the exact pre-defined task templates from FSPro Labs Event Log Explorer.
"""

from typing import List, Dict
from .models import TaskTemplate

TASK_TEMPLATES: List[TaskTemplate] = [
    # --- Audit Templates ---
    TaskTemplate(
        template_id="audit_rdp_logons",
        category="Audit",
        name="Audit RDP logons",
        description="Tracks Remote Desktop Protocol (RDP) logons, connections, and sessions.",
        target_channel="Security",
        event_ids=[4624, 4625, 1149, 21, 24, 25],
        levels=["Audit Success", "Audit Failure", "Information"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=4624 or EventID=4625)] and EventData[Data[@Name='LogonType']='10']]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="audit_logons",
        category="Audit",
        name="Audit logons",
        description="Monitors all user account authentication and logon events.",
        target_channel="Security",
        event_ids=[4624, 4625, 4634, 4648, 4672],
        levels=["Audit Success", "Audit Failure"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=4624 or EventID=4625 or EventID=4634 or EventID=4648 or EventID=4672)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="audit_failures",
        category="Audit",
        name="Audit failures",
        description="Captures failed authentication attempts and brute-force indicators.",
        target_channel="Security",
        event_ids=[4625, 4776],
        levels=["Audit Failure"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=4625 or EventID=4776)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="audit_interactive_logons",
        category="Audit",
        name="Audit interactive logons",
        description="Monitors direct console and workstation interactive user logins.",
        target_channel="Security",
        event_ids=[4624, 4625],
        levels=["Audit Success", "Audit Failure"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=4624 or EventID=4625)] and EventData[Data[@Name='LogonType']='2']]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="clear_event_log",
        category="Audit",
        name="Clear event log",
        description="Alerts when an audit or system event log is cleared (Tamper Detection).",
        target_channel="Security",
        event_ids=[1102, 104],
        levels=["Audit Success", "Information", "Warning"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=1102)]]</Select>
    <Select Path="System">*[System[(EventID=104)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="clear_security_log",
        category="Audit",
        name="Clear security log",
        description="Detects Event ID 1102 indicating the Security audit log was wiped.",
        target_channel="Security",
        event_ids=[1102],
        levels=["Audit Success"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=1102)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="user_account_mgmt",
        category="Audit",
        name="User account management",
        description="Monitors user creation, deletion, password resets, and changes.",
        target_channel="Security",
        event_ids=[4720, 4722, 4724, 4725, 4726, 4738],
        levels=["Audit Success"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID &gt;= 4720 and EventID &lt;= 4738)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="member_added_group",
        category="Audit",
        name="Member added to group",
        description="Detects privilege escalation when accounts are added to Administrators.",
        target_channel="Security",
        event_ids=[4728, 4732, 4756],
        levels=["Audit Success"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=4728 or EventID=4732 or EventID=4756)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="file_deletion",
        category="Audit",
        name="File deletion",
        description="Audit file and object deletion events.",
        target_channel="Security",
        event_ids=[4660, 4663],
        levels=["Audit Success"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=4660 or EventID=4663)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="audit_policy_change",
        category="Audit",
        name="Audit policy change",
        description="Monitors changes to audit logging policies.",
        target_channel="Security",
        event_ids=[4719, 4739],
        levels=["Audit Success"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Security">*[System[(EventID=4719 or EventID=4739)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="audit_printer_usage",
        category="Audit",
        name="Audit printer usage",
        description="Tracks documents printed on local or network printers.",
        target_channel="Microsoft-Windows-PrintService/Operational",
        event_ids=[307],
        levels=["Information"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Microsoft-Windows-PrintService/Operational">*[System[(EventID=307)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="new_external_device",
        category="Audit",
        name="New external device",
        description="Identifies USB device connection and driver installation.",
        target_channel="System",
        event_ids=[20001, 20003, 10000],
        levels=["Information"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="System">*[System[(EventID=20001 or EventID=20003)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="rdp_reconnects",
        category="Audit",
        name="RDP logons and reconnects",
        description="Tracks Remote Desktop reconnection and session reconnect events.",
        target_channel="Microsoft-Windows-TerminalServices-LocalSessionManager/Operational",
        event_ids=[21, 22, 24, 25],
        levels=["Information"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="Microsoft-Windows-TerminalServices-LocalSessionManager/Operational">*[System[(EventID &gt;= 21 and EventID &lt;= 25)]]</Select>
  </Query>
</QueryList>'''
    ),
    # --- System Templates ---
    TaskTemplate(
        template_id="boot_shutdown",
        category="System",
        name="System boot & shutdown",
        description="Chronological record of system start, reboot, clean & unexpected shutdowns.",
        target_channel="System",
        event_ids=[6005, 6006, 6008, 1074, 41],
        levels=["Information", "Warning", "Critical"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="System">*[System[(EventID=6005 or EventID=6006 or EventID=6008 or EventID=1074 or EventID=41)]]</Select>
  </Query>
</QueryList>'''
    ),
    TaskTemplate(
        template_id="services_crashes",
        category="System",
        name="Service installation & crashes",
        description="Service state transitions, new service installations, and crashes.",
        target_channel="System",
        event_ids=[7045, 7036, 7040, 1000, 1002],
        levels=["Information", "Warning", "Error"],
        xml_query='''<QueryList>
  <Query Id="0">
    <Select Path="System">*[System[(EventID=7045 or EventID=7036 or EventID=7040 or EventID=1000)]]</Select>
  </Query>
</QueryList>'''
    ),
]


def get_templates_by_category() -> Dict[str, List[TaskTemplate]]:
    result = {}
    for t in TASK_TEMPLATES:
        result.setdefault(t.category, []).append(t)
    return result
