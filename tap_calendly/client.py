"""REST client handling, including CalendlyStream base class."""

from __future__ import annotations

import sys
from typing import Any, Callable, Iterable

import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, JSONPathPaginator
from singer_sdk.streams import RESTStream

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]

SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"

class CalendlyStream(RESTStream):

    records_jsonpath = "$.collection[*]"
    next_page_token_jsonpath = "$.pagination.next_page_token"  

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
        """Create a new pagination helper instance."""

        return JSONPathPaginator(self.next_page_token_jsonpath)


    def get_url_params(self, context: dict | None, next_page_token: Any | None) -> dict[str, Any]:
        params = {}

        last_updated = self.get_starting_replication_key_value(context)

        if last_updated:
            params["start_time"] = last_updated

        if next_page_token:
            params['page_token'] = next_page_token
            
        params["organization"] = self.config.get("organization_url")
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.
        """
        if response.status_code != 200:
            logger.error(f"API call failed: {response.status_code} - {response.text}")
            return  # You might want to raise an exception or handle this case differently depending on your use case
        logger.info("API call successful, parsing response")
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

