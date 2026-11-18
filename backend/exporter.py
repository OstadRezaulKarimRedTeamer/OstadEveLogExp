"""
Event Log Explorer - Exporter Engine
Exports event logs to CSV, JSON, XML, and Standalone HTML Reports.
"""

import csv
import json
import html
from typing import List
from .models import EventRecord


class EventExporter:
    """Exports EventRecord lists to various standard formats."""

    @staticmethod
    def export_csv(records: List[EventRecord], filepath: str) -> None:
        fieldnames = [
            "RecordID", "DateTime", "Level", "EventID", "Source",
            "TaskCategory", "User", "Computer", "Description", "Keywords"
        ]
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow({
                    "RecordID": r.record_id,
                    "DateTime": r.time_created_str,
                    "Level": r.level_name,
                    "EventID": r.event_id,
                    "Source": r.provider_name,
                    "TaskCategory": r.task_category,
                    "User": r.user_name,
                    "Computer": r.computer,
                    "Description": r.description.replace("\n", " "),
                    "Keywords": r.keywords
                })

    @staticmethod
    def export_json(records: List[EventRecord], filepath: str) -> None:
        data = []
        for r in records:
            data.append({
                "record_id": r.record_id,
                "time_created": r.time_created_str,
                "level": r.level_name,
                "event_id": r.event_id,
                "source": r.provider_name,
                "task_category": r.task_category,
                "user": r.user_name,
                "computer": r.computer,
                "description": r.description,
                "event_data": r.event_data,
                "keywords": r.keywords
            })
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def export_xml(records: List[EventRecord], filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<Events>\n')
            for r in records:
                f.write(r.xml_raw.strip() + "\n")
            f.write("</Events>\n")

    @staticmethod
    def export_html_report(records: List[EventRecord], filepath: str, title: str = "Windows Event Log Report") -> None:
        # Calculate summary statistics
        total = len(records)
        level_counts = {}
        for r in records:
            level_counts[r.level_name] = level_counts.get(r.level_name, 0) + 1

        rows_html = []
        for r in records:
            # Row badge color class
            lvl = r.level_name.lower().replace(" ", "-")
            rows_html.append(f"""
            <tr class="row-{lvl}">
                <td><span class="badge badge-{lvl}">{html.escape(r.level_name)}</span></td>
                <td style="white-space:nowrap;">{html.escape(r.time_created_str)}</td>
                <td><strong>{r.event_id}</strong></td>
                <td>{html.escape(r.provider_name)}</td>
                <td>{html.escape(r.user_name)}</td>
                <td>{html.escape(r.computer)}</td>
                <td class="desc-cell" title="{html.escape(r.description)}">{html.escape(r.description[:180])}</td>
            </tr>
            """)

        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 24px; background: #f8fafc; color: #1e293b; }}
    h1 {{ margin: 0 0 8px 0; font-size: 24px; color: #0f172a; }}
    .subtitle {{ color: #64748b; margin-bottom: 20px; font-size: 14px; }}
    .stats-container {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
    .stat-card {{ background: white; padding: 14px 20px; border-radius: 8px; border: 1px solid #e2e8f0; min-width: 140px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
    .stat-val {{ font-size: 24px; font-weight: bold; color: #0284c7; margin-top: 4px; }}
    .stat-lbl {{ font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
    .search-bar {{ width: 100%; box-sizing: border-box; padding: 10px 14px; font-size: 14px; border: 1px solid #cbd5e1; border-radius: 6px; margin-bottom: 16px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
    th {{ background: #f1f5f9; text-align: left; padding: 10px 12px; font-size: 13px; font-weight: 600; color: #334155; border-bottom: 1px solid #e2e8f0; }}
    td {{ padding: 8px 12px; font-size: 13px; border-bottom: 1px solid #f1f5f9; }}
    tr:hover {{ background-color: #f8fafc; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }}
    .badge-error {{ background: #fee2e2; color: #991b1b; }}
    .badge-critical {{ background: #991b1b; color: white; }}
    .badge-warning {{ background: #fef3c7; color: #92400e; }}
    .badge-information {{ background: #e0f2fe; color: #0369a1; }}
    .badge-audit-success {{ background: #dcfce7; color: #166534; }}
    .badge-audit-failure {{ background: #fce7f3; color: #9d174d; }}
    .desc-cell {{ max-width: 450px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
</style>
</head>
<body>
    <h1>{html.escape(title)}</h1>
    <div class="subtitle">Generated by Event Log Explorer Clone &bull; Total records: {total}</div>
    
    <div class="stats-container">
        <div class="stat-card"><div class="stat-lbl">Total Events</div><div class="stat-val">{total}</div></div>
        <div class="stat-card"><div class="stat-lbl">Errors</div><div class="stat-val" style="color:#b91c1c;">{level_counts.get("Error", 0)}</div></div>
        <div class="stat-card"><div class="stat-lbl">Warnings</div><div class="stat-val" style="color:#d97706;">{level_counts.get("Warning", 0)}</div></div>
        <div class="stat-card"><div class="stat-lbl">Information</div><div class="stat-val" style="color:#0284c7;">{level_counts.get("Information", 0)}</div></div>
        <div class="stat-card"><div class="stat-lbl">Audit Failures</div><div class="stat-val" style="color:#be185d;">{level_counts.get("Audit Failure", 0)}</div></div>
    </div>

    <input type="text" id="filterInput" class="search-bar" placeholder="Type here to filter table rows in real-time (Event ID, Provider, Description, User)..." onkeyup="filterTable()">

    <table id="eventTable">
        <thead>
            <tr>
                <th>Level</th>
                <th>Date & Time</th>
                <th>Event ID</th>
                <th>Source / Provider</th>
                <th>User</th>
                <th>Computer</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            {"".join(rows_html)}
        </tbody>
    </table>

    <script>
    function filterTable() {{
        var input = document.getElementById("filterInput");
        var filter = input.value.toLowerCase();
        var table = document.getElementById("eventTable");
        var tr = table.getElementsByTagName("tr");
        for (var i = 1; i < tr.length; i++) {{
            var text = tr[i].textContent || tr[i].innerText;
            if (text.toLowerCase().indexOf(filter) > -1) {{
                tr[i].style.display = "";
            }} else {{
                tr[i].style.display = "none";
            }}
        }}
    }}
    </script>
</body>
</html>
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
