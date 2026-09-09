"""Adquisición universal: CSV de osciloscopio, JSON de central y registros."""

from .pipeline import ImportResult, process_campaign
from .parser import ParsedTable, parse_csv, parse_json_campaign, suggest_mapping

__all__ = [
    "ImportResult",
    "ParsedTable",
    "parse_csv",
    "parse_json_campaign",
    "process_campaign",
    "suggest_mapping",
]
