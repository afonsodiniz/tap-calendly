"""REST client handling, including CalendlyStream base class."""

from __future__ import annotations

import sys
from typing import Any, Callable, Iterable

import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator  # noqa: TCH002
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]

SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"

class CalendlyStream(RESTStream):

    records_jsonpath = "$.collection[*]"
    next_page_token_jsonpath = "$.next_page"

    @property
    def url_base(self) -> str:
        """Return the base_url, configurable via tap settings."""
        
        return self.config.get("base_url", "https://api.calendly.com")

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object. """
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=self.config.get("auth_token", ""),
        )

    @property
    def http_headers(self) -> dict:
        """Return the HTTP headers needed for the API requests."""
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.get('auth_token', '')}"
        }
        return headers


    def get_new_paginator(self) -> BaseAPIPaginator:
        return super().get_new_paginator()


    def get_url_params( self, context: dict | None, next_page_token: Any | None) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization. """
        
        params = super().get_url_params(context, next_page_token)
        params["organization"] = self.config.get("organization_url")
        return params


    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

