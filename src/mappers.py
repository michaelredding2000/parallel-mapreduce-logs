"""
Built-in map functions for common log-analysis tasks.

Each mapper takes one log line (str) and returns a list of (key, value) pairs,
or an empty list if the line should be skipped.

Expected log format (Combined Log Format / Apache-style):
    127.0.0.1 - frank [10/Oct/2024:13:55:36 -0700] "GET /index.html HTTP/1.1" 200 2326
"""

from __future__ import annotations

import re

# Regex for Combined Log Format
_LOG_RE = re.compile(
    r'(?P<ip>\S+)'             # client IP
    r'\s+\S+\s+\S+\s+'        # ident, user
    r'\[(?P<datetime>[^\]]+)\]'  # [timestamp]
    r'\s+"(?P<method>\S+)\s+(?P<path>\S+)[^"]*"'  # "METHOD /path HTTP/x.x"
    r'\s+(?P<status>\d{3})'   # status code
    r'\s+(?P<bytes>\S+)'      # bytes sent
)


def parse_line(line: str) -> re.Match | None:
    """Return a regex match for a Combined-Log-Format line, or None."""
    return _LOG_RE.match(line.strip())


# ------------------------------------------------------------------
def status_code_mapper(line: str) -> list[tuple[str, int]]:
    """Emit (status_code, 1) for each request."""
    m = parse_line(line)
    if not m:
        return []
    return [(m.group("status"), 1)]


def method_mapper(line: str) -> list[tuple[str, int]]:
    """Emit (HTTP_method, 1) for each request."""
    m = parse_line(line)
    if not m:
        return []
    return [(m.group("method"), 1)]


def ip_mapper(line: str) -> list[tuple[str, int]]:
    """Emit (client_ip, 1) for each request."""
    m = parse_line(line)
    if not m:
        return []
    return [(m.group("ip"), 1)]


def hourly_mapper(line: str) -> list[tuple[str, int]]:
    """
    Emit (YYYY-MM-DD HH:00, 1) for each request so you can count
    requests per hour.
    """
    m = parse_line(line)
    if not m:
        return []
    # datetime like: 10/Oct/2024:13:55:36 -0700
    dt_str = m.group("datetime")
    try:
        date_part, time_part = dt_str.split(":", 1)
        hour = time_part.split(":")[0]
        day, month_abbr, year = date_part.split("/")
        key = f"{year}-{month_abbr}-{day.zfill(2)} {hour}:00"
    except (ValueError, IndexError):
        return []
    return [(key, 1)]


def error_mapper(line: str) -> list[tuple[str, int]]:
    """Emit ('error', 1) only for 4xx/5xx responses."""
    m = parse_line(line)
    if not m:
        return []
    status = int(m.group("status"))
    if status >= 400:
        return [("error", 1)]
    return []
