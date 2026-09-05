"""Tests for log-line mappers."""

import pytest
from src.mappers import (
    status_code_mapper,
    method_mapper,
    ip_mapper,
    hourly_mapper,
    error_mapper,
    parse_line,
)

# A valid Combined Log Format line
VALID_LINE = (
    '192.168.1.1 - alice [10/Oct/2024:13:55:36 -0700] '
    '"GET /index.html HTTP/1.1" 200 2326'
)

ERROR_LINE = (
    '10.0.0.2 - - [10/Oct/2024:14:01:00 -0700] '
    '"POST /login HTTP/1.1" 403 512'
)

SERVER_ERROR_LINE = (
    '10.0.0.3 - - [10/Oct/2024:15:00:00 -0700] '
    '"GET /api/data HTTP/1.1" 500 0'
)

MALFORMED_LINE = "this is not a log line at all"


class TestParseLine:
    def test_parses_valid(self):
        m = parse_line(VALID_LINE)
        assert m is not None
        assert m.group("ip") == "192.168.1.1"
        assert m.group("status") == "200"
        assert m.group("method") == "GET"

    def test_returns_none_for_malformed(self):
        assert parse_line(MALFORMED_LINE) is None

    def test_returns_none_for_empty(self):
        assert parse_line("") is None


class TestStatusCodeMapper:
    def test_emits_status_200(self):
        pairs = status_code_mapper(VALID_LINE)
        assert pairs == [("200", 1)]

    def test_emits_status_403(self):
        pairs = status_code_mapper(ERROR_LINE)
        assert pairs == [("403", 1)]

    def test_skips_malformed(self):
        assert status_code_mapper(MALFORMED_LINE) == []


class TestMethodMapper:
    def test_get(self):
        assert method_mapper(VALID_LINE) == [("GET", 1)]

    def test_post(self):
        assert method_mapper(ERROR_LINE) == [("POST", 1)]

    def test_skips_malformed(self):
        assert method_mapper(MALFORMED_LINE) == []


class TestIpMapper:
    def test_emits_ip(self):
        assert ip_mapper(VALID_LINE) == [("192.168.1.1", 1)]

    def test_skips_malformed(self):
        assert ip_mapper(MALFORMED_LINE) == []


class TestHourlyMapper:
    def test_emits_hour_bucket(self):
        pairs = hourly_mapper(VALID_LINE)
        assert len(pairs) == 1
        key, val = pairs[0]
        assert val == 1
        assert "13:00" in key
        assert "2024" in key

    def test_skips_malformed(self):
        assert hourly_mapper(MALFORMED_LINE) == []


class TestErrorMapper:
    def test_no_emit_for_200(self):
        assert error_mapper(VALID_LINE) == []

    def test_emits_for_403(self):
        assert error_mapper(ERROR_LINE) == [("error", 1)]

    def test_emits_for_500(self):
        assert error_mapper(SERVER_ERROR_LINE) == [("error", 1)]

    def test_skips_malformed(self):
        assert error_mapper(MALFORMED_LINE) == []
