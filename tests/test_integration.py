import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from src.openapi_mcp_gen.cli import cli


class TestIntegration:
    """Integration tests for the authentication feature."""

    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.sample_openapi = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test endpoint",
                        "responses": {"200": {"description": "Success"}},
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "BasicAuth": {"type": "http", "scheme": "basic"},
                    "BearerAuth": {"type": "http", "scheme": "bearer"},
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                    },
                }
            },
        }

    def create_temp_openapi_file(self, content):
        """Create a temporary OpenAPI file."""
        import yaml

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False)
        yaml.dump(content, temp_file)
        temp_file.close()
        return temp_file.name

    @patch("src.openapi_mcp_gen.server.FastMCP")
    @patch("src.openapi_mcp_gen.server.httpx")
    def test_integration_basic_auth_flow(self, mock_httpx, mock_fastmcp):
        """Test complete flow with basic authentication."""
        # Create temporary OpenAPI file
        temp_file = self.create_temp_openapi_file(self.sample_openapi)

        try:
            mock_client = mock_httpx.AsyncClient.return_value
            mock_server = mock_fastmcp.from_openapi.return_value

            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--path",
                    temp_file,
                    "--auth-type",
                    "basic",
                    "--basic-username",
                    "testuser",
                    "--basic-password",
                    "testpass",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8080",
                ],
            )

            # Should complete successfully
            assert result.exit_code == 0

            # Verify authentication was applied
            assert "Using authentication type: basic" in result.output

            # Verify server components were called
            mock_httpx.AsyncClient.assert_called_once()
            mock_fastmcp.from_openapi.assert_called_once()
            mock_server.run.assert_called_once()

        finally:
            os.unlink(temp_file)

    @patch("src.openapi_mcp_gen.server.FastMCP")
    @patch("src.openapi_mcp_gen.server.httpx")
    def test_integration_bearer_auth_flow(self, mock_httpx, mock_fastmcp):
        """Test complete flow with bearer authentication."""
        temp_file = self.create_temp_openapi_file(self.sample_openapi)

        try:
            mock_client = mock_httpx.AsyncClient.return_value
            mock_server = mock_fastmcp.from_openapi.return_value

            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--path",
                    temp_file,
                    "--auth-type",
                    "bearer",
                    "--bearer-token",
                    "test-token-123",
                    "--base-url",
                    "https://api.example.com",
                ],
            )

            assert result.exit_code == 0
            assert "Using authentication type: bearer" in result.output
            assert "Using base URL: https://api.example.com" in result.output

        finally:
            os.unlink(temp_file)

    @patch("src.openapi_mcp_gen.server.FastMCP")
    @patch("src.openapi_mcp_gen.server.httpx")
    def test_integration_api_key_auth_flow(self, mock_httpx, mock_fastmcp):
        """Test complete flow with API key authentication."""
        temp_file = self.create_temp_openapi_file(self.sample_openapi)

        try:
            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--path",
                    temp_file,
                    "--auth-type",
                    "api_key",
                    "--api-key-location",
                    "header",
                    "--api-key-name",
                    "X-API-Key",
                    "--api-key-value",
                    "secret-key-value",
                ],
            )

            assert result.exit_code == 0
            assert "Using authentication type: api_key" in result.output

        finally:
            os.unlink(temp_file)

    def test_integration_validation_errors(self):
        """Test that validation errors are properly handled."""
        temp_file = self.create_temp_openapi_file(self.sample_openapi)

        try:
            # Test missing basic auth password
            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--path",
                    temp_file,
                    "--auth-type",
                    "basic",
                    "--basic-username",
                    "user",
                    # Missing password
                ],
            )

            assert result.exit_code != 0
            assert (
                "Basic authentication requires both username and password"
                in result.output
            )

        finally:
            os.unlink(temp_file)

    def test_integration_no_auth(self):
        """Test that the system works without authentication."""
        temp_file = self.create_temp_openapi_file(self.sample_openapi)

        try:
            with patch("src.openapi_mcp_gen.server.FastMCP") as mock_fastmcp:
                with patch("src.openapi_mcp_gen.server.httpx") as mock_httpx:
                    result = self.runner.invoke(cli, ["generate", "--path", temp_file])

                    assert result.exit_code == 0

                    # Verify no auth type mentioned
                    assert "Using authentication type:" not in result.output

                    # Verify httpx client created without auth
                    mock_httpx.AsyncClient.assert_called_once_with(
                        base_url=None, auth=None
                    )

        finally:
            os.unlink(temp_file)

    def test_auth_handler_integration(self):
        """Test AuthHandler integration with different auth types."""
        import httpx

        from src.openapi_mcp_gen.auth import AuthHandler

        # Test basic auth
        handler = AuthHandler("basic", ("user", "pass"))
        auth = handler.get_auth()
        assert isinstance(auth, httpx.BasicAuth)

        # Test bearer auth
        handler = AuthHandler("bearer", "token")
        auth = handler.get_auth()
        assert auth is not None

        # Test API key auth
        handler = AuthHandler("api_key", ("header", "X-API-Key", "value"))
        auth = handler.get_auth()
        assert auth is not None

        # Test OAuth2 auth
        handler = AuthHandler("oauth2", ("url", "id", "secret", "scope"))
        auth = handler.get_auth()
        assert auth is not None
