#!/usr/bin/env python3
"""Render self-contained, animated SVG artwork from contribution data."""
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
USER = html.escape(str(DATA["username"]))
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BG, PANEL, BORDER, MUTED, TEXT, GREEN, CYAN = "#0d1117", "#161b22", "#30363d", "#8b949e", "#e6edf3", "#39d353", "#58a6ff"
PALETTE = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]


def window(width: int, height: int, title: str) -> list[str]:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{MONO}">',
        '<style>@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.a{opacity:0;animation:rise .45s ease-out forwards}@media (prefers-reduced-motion:reduce){.a{opacity:1;animation:none}}</style>',
        f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/><rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{BORDER}"/>',
        f'<line x1="0" x2="{width}" y1="32" y2="32" stroke="{BORDER}"/>',
    ]
    for i, color in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        parts.append(f'<circle cx="{22 + i * 16}" cy="16" r="5" fill="{color}"/>')
    parts.append(f'<text x="{width / 2}" y="20" text-anchor="middle" fill="{MUTED}" font-size="12">{title}</text>')
    return parts


def grid() -> list[list[dict[str, object] | None]]:
    days = DATA["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    column: list[dict[str, object] | None] = [None] * ((first.weekday() + 1) % 7)
    columns: list[list[dict[str, object] | None]] = []
    for day in days:
        weekday = (dt.date.fromisoformat(day["date"]).weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)
        column.append(day)
        if len(column) == 7:
            columns.append(column)
            column = []
    if column:
        columns.append(column + [None] * (7 - len(column)))
    return columns


def render_heatmap() -> None:
    width, height, x0, y0, step = 860, 260, 48, 64, 15
    parts = window(width, height, f"{USER}@github: ~/contributions --graph")
    parts.append('<text x="20" y="93" fill="#8b949e" font-size="10">Mon</text><text x="20" y="123" fill="#8b949e" font-size="10">Wed</text><text x="20" y="153" fill="#8b949e" font-size="10">Fri</text>')
    seen: set[str] = set()
    for col, days in enumerate(grid()):
        for day in days:
            if day:
                date = dt.date.fromisoformat(str(day["date"]))
                key = date.strftime("%Y-%m")
                if key not in seen and date.day <= 7:
                    seen.add(key)
                    parts.append(f'<text x="{x0 + col * step}" y="53" fill="{MUTED}" font-size="10">{date.strftime("%b")}</text>')
                break
        for row, day in enumerate(days):
            if not day:
                continue
            level = min(int(day["level"]), len(PALETTE) - 1)
            delay = (col * .025) + (row * .04)
            x, y = x0 + col * step, y0 + row * step
            date, count = html.escape(str(day["date"])), int(day["count"])
            parts.append(f'<rect class="a" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="11" height="11" rx="2" fill="{PALETTE[level]}"><title>{date}: {count} contributions</title></rect>')
    parts += [
        f'<line x1="20" x2="840" y1="190" y2="190" stroke="{BORDER}"/>',
        f'<text x="20" y="220" fill="{TEXT}" font-size="15"><tspan fill="{GREEN}" font-weight="700">{int(DATA["total"]):,}</tspan> contributions in the last year</text>',
        f'<text x="840" y="220" text-anchor="end" fill="{MUTED}" font-size="13">current streak <tspan fill="{CYAN}" font-weight="700">{DATA["current_streak"]} days</tspan> · longest <tspan fill="{CYAN}" font-weight="700">{DATA["longest_streak"]} days</tspan></text>',
        '</svg>',
    ]
    (ROOT / "contributions.svg").write_text("".join(parts), encoding="utf-8")


def render_stats() -> None:
    width, height = 840, 360
    parts = window(width, height, f"{USER}@github: ~/stats")
    metrics = [("contributions", f'{int(DATA["total"]):,}'), ("active days", str(DATA["active_days"])), ("current streak", f'{DATA["current_streak"]} days'), ("longest streak", f'{DATA["longest_streak"]} days'), ("best day", str(DATA["best_day"])), ("activity", "public")]
    for index, (label, value) in enumerate(metrics):
        col, row = index % 2, index // 2
        x, y, delay = 20 + col * 402, 52 + row * 95, index * .12
        parts.append(f'<g class="a" style="animation-delay:{delay:.2f}s"><rect x="{x}" y="{y}" width="380" height="78" rx="8" fill="{PANEL}" stroke="{BORDER}"/><text x="{x+18}" y="{y+27}" fill="{MUTED}" font-size="13">$ {label}</text><text x="{x+18}" y="{y+60}" fill="{GREEN if index == 0 else TEXT}" font-size="25" font-weight="700">{value}</text></g>')
    parts.append('</svg>')
    (ROOT / "stats.svg").write_text("".join(parts), encoding="utf-8")


def render_identity() -> None:
    parts = window(840, 360, f"{USER}@github: ~/whoami")
    lines = ["THORSEN", "", "python builder", "applied AI", "music discovery"]
    for index, line in enumerate(lines):
        y = 100 + index * 46
        size = 42 if index == 0 else 22
        fill = GREEN if index == 0 else TEXT
        parts.append(f'<text class="a" style="animation-delay:{index*.18:.2f}s" x="48" y="{y}" fill="{fill}" font-size="{size}" font-weight="700">{line}</text>')
    parts.append(f'<text x="48" y="326" fill="{MUTED}" font-size="14">$ echo $BUILD_IN_PUBLIC</text></svg>')
    (ROOT / "identity.svg").write_text("".join(parts), encoding="utf-8")


if __name__ == "__main__":
    render_heatmap()
    render_stats()
    render_identity()
    print("rendered contributions.svg, stats.svg, identity.svg")
