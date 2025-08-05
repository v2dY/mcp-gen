import json
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Union

import httpx
import yaml
from fastmcp import FastMCP

from .auth import AuthHandler


class OpenAPISpecHandler:
    """Handle OpenAPI specification file operations."""

    @staticmethod
    def is_url(path: str) -> bool:
        """Check if the path is a URL."""
        parsed = urllib.parse.urlparse(path)
        return parsed.scheme in ("http", "https")

    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> Dict[Any, Any]:
        """Load OpenAPI spec from file by trying YAML first, then JSON."""
        with open(file_path, "r") as f:
            try:
                return yaml.safe_load(f)  # Try loading as YAML
            except yaml.YAMLError:
                f.seek(0)  # Reset file pointer
                return json.load(f)  # Fallback to JSON

    @staticmethod
    def load_from_content(content: str) -> Dict[Any, Any]:
        """Load OpenAPI spec from string content by trying YAML first, then JSON."""
        try:
            return yaml.safe_load(content)  # Try loading as YAML
        except yaml.YAMLError:
            return json.loads(content)  # Fallback to JSON

    @classmethod
    def download_from_url(cls, url: str) -> str:
        """Download OpenAPI specification from URL and return content as string."""
        # Validate URL
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid URL: {url}")

        # Only allow http and https schemes
        if parsed_url.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL: {url}")

        # Download the content
        with urllib.request.urlopen(url) as response:
            return response.read().decode("utf-8")

    @classmethod
    def load_from_path_or_url(cls, path_or_url: str) -> Dict[Any, Any]:
        """Load OpenAPI spec from either a file path or URL."""
        if cls.is_url(path_or_url):
            content = cls.download_from_url(path_or_url)
            return cls.load_from_content(content)
        else:
            file_path = Path(path_or_url)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path_or_url}")
            return cls.load_from_file(file_path)


def load_openapi_spec(file_path):
    """Load OpenAPI spec by trying YAML first, then JSON.

    Deprecated: Use OpenAPISpecHandler.load_from_file() instead.
    """
    return OpenAPISpecHandler.load_from_file(file_path)


def create_and_run_mcp_server(
    openapi_spec: Union[Dict[Any, Any], str],
    host="0.0.0.0",
    port=8000,
    name="Generated MCP Server",
    base_url=None,
    auth_type=None,
    credentials=None,
):
    """Create and run a FastMCP server from an OpenAPI spec content."""
    # Handle both dict (already parsed) and string content
    if isinstance(openapi_spec, str):
        spec_dict = OpenAPISpecHandler.load_from_content(openapi_spec)
    else:
        spec_dict = openapi_spec

    # Handle authentication
    auth_handler = AuthHandler(auth_type, credentials)
    auth = auth_handler.get_auth()

    # Create client with base_url and auth if provided
    client = httpx.AsyncClient(base_url=base_url, auth=auth)

    mcp_server = FastMCP.from_openapi(openapi_spec=spec_dict, client=client, name=name)

    mcp_server.run(transport="http", host=host, port=port)
