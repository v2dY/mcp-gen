from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from src.openapi_mcp_gen.cli import cli, generate


class TestCLI:
    """Test suite for CLI functionality."""

    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "OpenAPI to MCP Generator" in result.output

    def test_generate_help(self):
        """Test generate command help."""
        result = self.runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "Generate an MCP server" in result.output

    def test_generate_missing_path(self):
        """Test generate command without required path."""
        result = self.runner.invoke(cli, ["generate"])
        assert result.exit_code != 0
        assert "Missing option" in result.output

    @patch("src.openapi_mcp_gen.cli.create_and_run_mcp_server")
    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_basic_command(self, mock_load_spec, mock_server):
        """Test basic generate command."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(cli, ["generate", "--path", "test.yml"])

        assert result.exit_code == 0
        mock_server.assert_called_once()

    @patch("src.openapi_mcp_gen.cli.create_and_run_mcp_server")
    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_with_basic_auth(self, mock_load_spec, mock_server):
        """Test generate command with basic authentication."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--auth-type",
                "basic",
                "--basic-username",
                "user",
                "--basic-password",
                "pass",
            ],
        )

        assert result.exit_code == 0
        # Verify the server was called with correct auth parameters
        args, kwargs = mock_server.call_args
        assert kwargs["auth_type"] == "basic"
        assert kwargs["credentials"] == ("user", "pass")

    @patch("src.openapi_mcp_gen.cli.create_and_run_mcp_server")
    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_with_bearer_auth(self, mock_load_spec, mock_server):
        """Test generate command with bearer authentication."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--auth-type",
                "bearer",
                "--bearer-token",
                "test-token",
            ],
        )

        assert result.exit_code == 0
        args, kwargs = mock_server.call_args
        assert kwargs["auth_type"] == "bearer"
        assert kwargs["credentials"] == "test-token"

    @patch("src.openapi_mcp_gen.cli.create_and_run_mcp_server")
    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_with_api_key_auth(self, mock_load_spec, mock_server):
        """Test generate command with API key authentication."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--auth-type",
                "api_key",
                "--api-key-location",
                "header",
                "--api-key-name",
                "X-API-Key",
                "--api-key-value",
                "test-key",
            ],
        )

        assert result.exit_code == 0
        args, kwargs = mock_server.call_args
        assert kwargs["auth_type"] == "api_key"
        assert kwargs["credentials"] == ("header", "X-API-Key", "test-key")

    @patch("src.openapi_mcp_gen.cli.create_and_run_mcp_server")
    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_with_oauth2_auth(self, mock_load_spec, mock_server):
        """Test generate command with OAuth2 authentication."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--auth-type",
                "oauth2",
                "--oauth-token-url",
                "https://auth.example.com/token",
                "--oauth-client-id",
                "client-id",
                "--oauth-client-secret",
                "client-secret",
                "--oauth-scope",
                "read write",
            ],
        )

        assert result.exit_code == 0
        args, kwargs = mock_server.call_args
        assert kwargs["auth_type"] == "oauth2"
        assert kwargs["credentials"] == (
            "https://auth.example.com/token",
            "client-id",
            "client-secret",
            "read write",
        )

    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_basic_auth_missing_username(self, mock_load_spec):
        """Test basic auth validation - missing username."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--auth-type",
                "basic",
                "--basic-password",
                "pass",
            ],
        )

        assert result.exit_code != 0
        assert (
            "Basic authentication requires both username and password" in result.output
        )

    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_bearer_auth_missing_token(self, mock_load_spec):
        """Test bearer auth validation - missing token."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli, ["generate", "--path", "test.yml", "--auth-type", "bearer"]
        )

        assert result.exit_code != 0
        assert "Bearer authentication requires a token" in result.output

    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_api_key_auth_missing_params(self, mock_load_spec):
        """Test API key auth validation - missing parameters."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--auth-type",
                "api_key",
                "--api-key-name",
                "X-API-Key",
            ],
        )

        assert result.exit_code != 0
        assert (
            "API key authentication requires location, name, and value" in result.output
        )

    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_oauth2_auth_missing_params(self, mock_load_spec):
        """Test OAuth2 auth validation - missing parameters."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--auth-type",
                "oauth2",
                "--oauth-client-id",
                "client-id",
            ],
        )

        assert result.exit_code != 0
        assert (
            "OAuth2 authentication requires token URL, client ID, client secret, and scope"
            in result.output
        )

    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_file_not_found(self, mock_load_spec):
        """Test generate command with non-existent file."""
        mock_load_spec.side_effect = FileNotFoundError(
            "[Errno 2] No such file or directory: 'nonexistent.yml'"
        )

        result = self.runner.invoke(cli, ["generate", "--path", "nonexistent.yml"])

        assert result.exit_code != 0
        assert "No such file or directory" in result.output

    @patch("src.openapi_mcp_gen.cli.create_and_run_mcp_server")
    @patch("src.openapi_mcp_gen.cli.OpenAPISpecHandler.load_from_path_or_url")
    def test_generate_with_all_options(self, mock_load_spec, mock_server):
        """Test generate command with all available options."""
        mock_load_spec.return_value = {
            "openapi": "3.0.0",
            "info": {"title": "Test API"},
        }

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "--path",
                "test.yml",
                "--base-url",
                "https://api.example.com",
                "--host",
                "127.0.0.1",
                "--port",
                "8080",
                "--server-name",
                "Test Server",
                "--auth-type",
                "bearer",
                "--bearer-token",
                "test-token",
            ],
        )

        assert result.exit_code == 0
        args, kwargs = mock_server.call_args
        assert kwargs["base_url"] == "https://api.example.com"
        assert kwargs["host"] == "127.0.0.1"
        assert kwargs["port"] == 8080
        assert kwargs["name"] == "Test Server"
        assert kwargs["auth_type"] == "bearer"
        assert kwargs["credentials"] == "test-token"
