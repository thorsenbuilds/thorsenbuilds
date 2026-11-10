#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar without credentials."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USER = os.environ.get("GH_PROFILE_USER", "thorsenbuilds")
URL = f"https://github.com/users/{USER}/contributions"
OUT = ROOT / "data" / "contributions.json"


class ContributionParser(HTMLParser):
    """Extract calendar cells and their tooltip labels from GitHub's public HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.cells: list[dict[str, str]] = []
        self.tooltips: dict[str, str] = {}
        self.active_tooltip: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "td" and "ContributionCalendar-day" in data.get("class", "") and data.get("data-date"):
            self.cells.append(data)
        elif tag == "tool-tip" and data.get("for"):
            self.active_tooltip = data["for"]
            self.tooltips[self.active_tooltip] = ""

    def handle_data(self, data: str) -> None:
        if self.active_tooltip:
            self.tooltips[self.active_tooltip] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "tool-tip":
            self.active_tooltip = None


def contribution_count(cell: dict[str, str], tooltips: dict[str, str]) -> int:
    label = tooltips.get(cell.get("id", ""), "")
    match = re.search(r"(\d+) contribution", label, re.I)
    return int(match.group(1)) if match else 0


def streak(days: list[dict[str, object]], longest: bool = False) -> int:
    if longest:
        best = run = 0
        for day in days:
            run = run + 1 if int(day["count"]) else 0
            best = max(best, run)
        return best
    index = len(days) - 1
    if index >= 0 and not int(days[index]["count"]):
        index -= 1
    length = 0
    while index >= 0 and int(days[index]["count"]):
        length += 1
        index -= 1
    return length


def main() -> None:
    request = Request(URL, headers={"User-Agent": "thorsenbuilds-profile/1.0"})
    with urlopen(request, timeout=30) as response:
        parser = ContributionParser()
        parser.feed(response.read().decode("utf-8"))
    days = [
        {"date": cell["data-date"], "count": contribution_count(cell, parser.tooltips), "level": int(cell.get("data-level", 0))}
        for cell in parser.cells
    ]
    if not days:
        raise RuntimeError("GitHub returned no contribution-calendar days")
    days.sort(key=lambda day: str(day["date"]))
    totals = [int(day["count"]) for day in days]
    monthly: dict[str, int] = {}
    for day in days:
        month = str(day["date"])[:7]
        monthly[month] = monthly.get(month, 0) + int(day["count"])
    payload = {
        "username": USER,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "days": days,
        "total": sum(totals),
        "active_days": sum(count > 0 for count in totals),
        "current_streak": streak(days),
        "longest_streak": streak(days, longest=True),
        "best_day": max(totals),
        "monthly": [{"month": month, "total": total} for month, total in sorted(monthly.items())],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"fetched {len(days)} days: {payload['total']} contributions")


if __name__ == "__main__":
    main()
