#!/usr/bin/env python3
"""
Lightweight integration stubs for external tools (Airtable, Make.com).
Replace with real clients as needed.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AirtableClient:
    async def upsert_record(self, table: str, record: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.05)
        return {
            "table": table,
            "record": record,
            "operation": "upsert",
            "status": "stubbed",
        }


@dataclass
class MakeClient:
    async def trigger_scenario(self, scenario_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.05)
        return {
            "scenario_id": scenario_id,
            "data": data,
            "status": "triggered_stub",
        }


def get_airtable_client() -> AirtableClient:
    return AirtableClient()


def get_make_client() -> MakeClient:
    return MakeClient()


