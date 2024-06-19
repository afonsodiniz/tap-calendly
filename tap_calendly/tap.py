from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  

from tap_calendly import streams

class TapCalendly(Tap):
    """Calendly tap class."""

    name = "tap-calendly"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_url",
            th.StringType,
            default="https://api.calendly.com/",
            description="The url for the API service",
        ),
        th.Property(
            "organization_url",
            th.StringType,
            default="https://api.calendly.com/organizations/1fdf0e87-f3cf-46bc-aa59-b97d16e8b75d/",
            description="Organization URL",
        ),
        th.Property(
            "auth_token",
            th.StringType,
            required=True,
            secret=True, 
            description="The token to authenticate against the API service",
        )

    ).to_dict()

    def discover_streams(self) -> list[streams.CalendlyStream]:
        """Return a list of discovered streams."""

        return [
            streams.ScheduledEvents(self)
        ]


if __name__ == "__main__":
    TapCalendly.cli()
