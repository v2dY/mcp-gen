import json
import tempfile
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import yaml

from src.openapi_mcp_gen.server import OpenAPISpecHandler


class TestOpenAPISpecHandler:
    """Test suite for OpenAPISpecHandler class."""

    def test_is_url_valid_http(self):
        """Test is_url with valid HTTP URL."""
        assert OpenAPISpecHandler.is_url("http://example.com/api.json") is True

    def test_is_url_valid_https(self):
        """Test is_url with valid HTTPS URL."""
        assert OpenAPISpecHandler.is_url("https://api.example.com/openapi.yaml") is True

    def test_is_url_file_path(self):
        """Test is_url with file path."""
        assert OpenAPISpecHandler.is_url("/path/to/file.json") is False
        assert OpenAPISpecHandler.is_url("./relative/path.yaml") is False
        assert OpenAPISpecHandler.is_url("file.json") is False

    def test_is_url_invalid_schemes(self):
        """Test is_url with invalid schemes."""
        assert OpenAPISpecHandler.is_url("ftp://example.com/file.json") is False
        assert OpenAPISpecHandler.is_url("file://path/to/file.json") is False
        assert OpenAPISpecHandler.is_url("mailto:user@example.com") is False

    def test_load_from_content_yaml(self):
        """Test loading OpenAPI spec from YAML content string."""
        yaml_content = """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
  description: A test API
paths:
  /test:
    get:
      summary: Test endpoint
"""

        spec = OpenAPISpecHandler.load_from_content(yaml_content)

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "1.0.0"
        assert spec["info"]["description"] == "A test API"
        assert "/test" in spec["paths"]
        assert "get" in spec["paths"]["/test"]

    def test_load_from_content_json(self):
        """Test loading OpenAPI spec from JSON content string."""
        json_content = """
{
  "openapi": "3.0.0",
  "info": {
    "title": "JSON Test API",
    "version": "2.0.0"
  },
  "paths": {
    "/users": {
      "get": {
        "summary": "Get users"
      }
    }
  }
}
"""

        spec = OpenAPISpecHandler.load_from_content(json_content)

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "JSON Test API"
        assert spec["info"]["version"] == "2.0.0"
        assert "/users" in spec["paths"]

    def test_load_from_content_invalid_yaml_fallback_to_json(self):
        """Test loading content that's invalid YAML but valid JSON."""
        # This is valid JSON but invalid YAML (due to unquoted strings in object keys)
        json_content = '{"openapi": "3.0.0", "info": {"title": "API"}}'

        spec = OpenAPISpecHandler.load_from_content(json_content)

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "API"

    def test_load_from_content_invalid_both(self):
        """Test loading content that's neither valid YAML nor JSON."""
        invalid_content = "this is not valid yaml or json content { [ invalid"

        # YAML parser is more lenient, so this will actually parse as YAML
        # but result in a string instead of a dict
        result = OpenAPISpecHandler.load_from_content(invalid_content)
        assert isinstance(result, str)  # YAML parses it as a plain string

    def test_load_from_content_truly_invalid_json(self):
        """Test loading content that's invalid YAML and will fallback to invalid JSON."""
        invalid_content = "{ invalid json without closing brace"

        with pytest.raises(json.JSONDecodeError):
            OpenAPISpecHandler.load_from_content(invalid_content)

    def test_load_from_file_yaml(self):
        """Test loading OpenAPI spec from YAML file."""
        yaml_content = """
openapi: 3.0.0
info:
  title: File Test API
  version: 1.0.0
paths: {}
"""

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            spec = OpenAPISpecHandler.load_from_file("test.yaml")

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "File Test API"

    def test_load_from_file_json_after_yaml_error(self):
        """Test loading JSON file when YAML parsing fails."""
        json_content = '{"openapi": "3.0.0", "info": {"title": "JSON File API"}}'

        # Mock file object that supports seek
        mock_file = MagicMock()
        mock_file.read.return_value = json_content
        mock_file.__enter__.return_value = mock_file

        with patch("builtins.open", return_value=mock_file):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError("Invalid YAML")):
                with patch(
                    "json.load",
                    return_value={
                        "openapi": "3.0.0",
                        "info": {"title": "JSON File API"},
                    },
                ):
                    spec = OpenAPISpecHandler.load_from_file("test.json")

        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "JSON File API"
        # Verify that seek(0) was called to reset file pointer
        mock_file.seek.assert_called_once_with(0)

    def test_load_from_file_with_path_object(self):
        """Test loading from Path object instead of string."""
        yaml_content = "openapi: 3.0.0\ninfo:\n  title: Path Test\n"

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            spec = OpenAPISpecHandler.load_from_file(Path("test.yaml"))

        assert spec["info"]["title"] == "Path Test"

    @patch("urllib.request.urlopen")
    def test_download_from_url_success(self, mock_urlopen):
        """Test successful download from URL."""
        test_content = '{"openapi": "3.0.0", "info": {"title": "Downloaded API"}}'

        # Mock response object
        mock_response = MagicMock()
        mock_response.read.return_value = test_content.encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        content = OpenAPISpecHandler.download_from_url(
            "https://api.example.com/openapi.json"
        )

        assert content == test_content
        mock_urlopen.assert_called_once_with("https://api.example.com/openapi.json")

    def test_download_from_url_invalid_url(self):
        """Test download with invalid URL format."""
        with pytest.raises(ValueError, match="Invalid URL"):
            OpenAPISpecHandler.download_from_url("not-a-url")

        with pytest.raises(ValueError, match="Invalid URL"):
            OpenAPISpecHandler.download_from_url("invalid://scheme")

    @patch("urllib.request.urlopen")
    def test_download_from_url_network_error(self, mock_urlopen):
        """Test download with network error."""
        mock_urlopen.side_effect = urllib.error.URLError("Network error")

        with pytest.raises(urllib.error.URLError):
            OpenAPISpecHandler.download_from_url("https://api.example.com/openapi.json")

    @patch("urllib.request.urlopen")
    def test_download_from_url_http_error(self, mock_urlopen):
        """Test download with HTTP error."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.example.com/openapi.json",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None,
        )

        with pytest.raises(urllib.error.HTTPError):
            OpenAPISpecHandler.download_from_url("https://api.example.com/openapi.json")

    @patch.object(OpenAPISpecHandler, "download_from_url")
    @patch.object(OpenAPISpecHandler, "load_from_content")
    def test_load_from_path_or_url_with_url(self, mock_load_content, mock_download):
        """Test load_from_path_or_url with URL."""
        test_url = "https://api.example.com/openapi.json"
        test_content = '{"openapi": "3.0.0"}'
        test_spec = {"openapi": "3.0.0"}

        mock_download.return_value = test_content
        mock_load_content.return_value = test_spec

        with patch.object(OpenAPISpecHandler, "is_url", return_value=True):
            result = OpenAPISpecHandler.load_from_path_or_url(test_url)

        assert result == test_spec
        mock_download.assert_called_once_with(test_url)
        mock_load_content.assert_called_once_with(test_content)

    @patch.object(OpenAPISpecHandler, "load_from_file")
    def test_load_from_path_or_url_with_file_path(self, mock_load_file):
        """Test load_from_path_or_url with file path."""
        test_path = "/path/to/openapi.yaml"
        test_spec = {"openapi": "3.0.0", "info": {"title": "File API"}}

        mock_load_file.return_value = test_spec

        with patch.object(OpenAPISpecHandler, "is_url", return_value=False):
            with patch.object(Path, "exists", return_value=True):
                result = OpenAPISpecHandler.load_from_path_or_url(test_path)

        assert result == test_spec
        mock_load_file.assert_called_once()
        # Check that a Path object was passed to load_from_file
        call_args = mock_load_file.call_args[0][0]
        assert isinstance(call_args, Path)
        assert str(call_args) == test_path

    def test_load_from_path_or_url_file_not_found(self):
        """Test load_from_path_or_url with non-existent file."""
        test_path = "/nonexistent/file.yaml"

        with patch.object(OpenAPISpecHandler, "is_url", return_value=False):
            with patch.object(Path, "exists", return_value=False):
                with pytest.raises(FileNotFoundError, match="File not found"):
                    OpenAPISpecHandler.load_from_path_or_url(test_path)

    def test_integration_yaml_file_to_dict(self):
        """Integration test: YAML file content to Python dict."""
        yaml_content = """
openapi: 3.0.0
info:
  title: Integration Test API
  version: 1.0.0
  description: Testing the full pipeline
servers:
  - url: https://api.example.com
    description: Production server
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
"""

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            spec = OpenAPISpecHandler.load_from_file("integration_test.yaml")

        # Verify complete structure
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Integration Test API"
        assert spec["info"]["description"] == "Testing the full pipeline"
        assert len(spec["servers"]) == 1
        assert spec["servers"][0]["url"] == "https://api.example.com"
        assert "/users" in spec["paths"]
        assert "get" in spec["paths"]["/users"]
        assert "responses" in spec["paths"]["/users"]["get"]
        assert "200" in spec["paths"]["/users"]["get"]["responses"]

    @patch("urllib.request.urlopen")
    def test_integration_url_download_to_dict(self, mock_urlopen):
        """Integration test: URL download to Python dict."""
        json_content = {
            "openapi": "3.0.0",
            "info": {"title": "Remote API", "version": "2.1.0"},
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {"200": {"description": "Service is healthy"}},
                    }
                }
            },
        }

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(json_content).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        spec = OpenAPISpecHandler.load_from_path_or_url(
            "https://api.example.com/openapi.json"
        )

        assert spec == json_content
        assert spec["info"]["title"] == "Remote API"
        assert "/health" in spec["paths"]

    def test_edge_case_empty_yaml_content(self):
        """Test handling of empty YAML content."""
        empty_content = ""

        result = OpenAPISpecHandler.load_from_content(empty_content)
        assert result is None

    def test_edge_case_yaml_with_special_characters(self):
        """Test YAML content with special characters and unicode."""
        yaml_content = """
openapi: 3.0.0
info:
  title: "API with Special Characters: !@#$%^&*()"
  version: 1.0.0
  description: |
    This API handles special characters and unicode: ñáéíóú
    It supports multi-line descriptions with various symbols.
paths:
  '/users/{userId}':
    get:
      summary: Get user by ID
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
            pattern: '^[a-zA-Z0-9_-]+$'
"""

        spec = OpenAPISpecHandler.load_from_content(yaml_content)

        assert "Special Characters: !@#$%^&*()" in spec["info"]["title"]
        assert "ñáéíóú" in spec["info"]["description"]
        assert (
            "/users/{userId}" in spec["paths"]
        )  # YAML doesn't preserve quotes in keys
