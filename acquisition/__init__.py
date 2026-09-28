"""Adquisición universal: CSV de osciloscopio, JSON de central y registros."""

from .parser import ParsedTable, parse_csv, parse_json_campaign, suggest_mapping
from .pipeline import ImportResult, process_campaign

__all__ = [
    "ImportResult",
    "ParsedTable",
    "parse_csv",
    "parse_json_campaign",
    "process_campaign",
    "suggest_mapping",
]
