"""Stream type classes for tap-calendly."""

from __future__ import annotations

import sys
import typing as t

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_calendly.client import CalendlyStream

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"

class ScheduledEvents(CalendlyStream):
    """Stream for ScheduledEvents endpoint"""

    name = "scheduled_events"
    path = "/scheduled_events"
    primary_keys = ["uri"]
    replication_key = "updated_at"
    schema_filepath = SCHEMAS_DIR / "scheduled_events.json"

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        context = context or {}

        uri = record.get("uri", "")
        uuid = uri.split('/')[-1]
        
        context["uuid"] = uuid

        return super().get_child_context(record, context) 

class Invitees(CalendlyStream):
    """Stream for Invitees endpoint"""

    name = "invitees"
    path = "/scheduled_events/{uuid}/invitees"
    primary_keys = ["uri"]
    replication_key = "updated_at"
    schema_filepath = SCHEMAS_DIR / "invitees.json"
    
    parent_stream_type = ScheduledEvents

    def post_process(self, row: dict, context: dict) -> dict | None:
        row["uuid"] = context["uuid"]
        return row
