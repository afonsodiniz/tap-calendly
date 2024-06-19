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
    primary_keys = ["id"]

    schema_filepath = SCHEMAS_DIR / "scheduled_events.json"  # noqa: ERA001
