import pytest
import json
import yaml
from unittest.mock import patch, mock_open, Mock
from pathlib import Path
from src.openapi_mcp_gen.server import load_openapi_spec, create_and_run_mcp_server


class TestServer:
    """Test suite for server functionality."""

    def test_load_openapi_spec_yaml(self):
        """Test loading OpenAPI spec from YAML file."""
        yaml_content = """
        openapi: 3.0.0
        info:
          title: Test API
          version: 1.0.0
        paths: {}
        """
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            spec = load_openapi_spec("test.yml")
            
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"

    def test_load_openapi_spec_json(self):
        """Test loading OpenAPI spec from JSON file."""
        json_content = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {}
        }
        
        # Mock yaml.safe_load to raise YAMLError to force JSON parsing
        with patch("builtins.open", mock_open(read_data=json.dumps(json_content))):
            with patch("yaml.safe_load", side_effect=yaml.YAMLError()):
                with patch("json.load", return_value=json_content):
                    spec = load_openapi_spec("test.json")
            
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"

    @patch('src.openapi_mcp_gen.server.FastMCP')
    @patch('src.openapi_mcp_gen.server.httpx')
    @patch('src.openapi_mcp_gen.server.load_openapi_spec')
    def test_create_and_run_mcp_server_basic(self, mock_load_spec, mock_httpx, mock_fastmcp):
        """Test basic MCP server creation without authentication."""
        mock_spec = {"openapi": "3.0.0", "info": {"title": "Test"}}
        mock_load_spec.return_value = mock_spec
        
        mock_client = Mock()
        mock_httpx.AsyncClient.return_value = mock_client
        
        mock_server = Mock()
        mock_fastmcp.from_openapi.return_value = mock_server
        
        create_and_run_mcp_server("test.yml")
        
        # Verify the spec was loaded
        mock_load_spec.assert_called_once_with("test.yml")
        
        # Verify client was created without auth
        mock_httpx.AsyncClient.assert_called_once_with(base_url=None, auth=None)
        
        # Verify MCP server was created
        mock_fastmcp.from_openapi.assert_called_once_with(
            openapi_spec=mock_spec,
            client=mock_client,
            name="Generated MCP Server"
        )
        
        # Verify server was started
        mock_server.run.assert_called_once_with(transport="http", host="0.0.0.0", port=8000)

    @patch('src.openapi_mcp_gen.server.FastMCP')
    @patch('src.openapi_mcp_gen.server.httpx')
    @patch('src.openapi_mcp_gen.server.load_openapi_spec')
    @patch('src.openapi_mcp_gen.server.AuthHandler')
    def test_create_and_run_mcp_server_with_auth(self, mock_auth_handler, mock_load_spec, mock_httpx, mock_fastmcp):
        """Test MCP server creation with authentication."""
        mock_spec = {"openapi": "3.0.0", "info": {"title": "Test"}}
        mock_load_spec.return_value = mock_spec
        
        mock_auth = Mock()
        mock_auth_instance = Mock()
        mock_auth_instance.get_auth.return_value = mock_auth
        mock_auth_handler.return_value = mock_auth_instance
        
        mock_client = Mock()
        mock_httpx.AsyncClient.return_value = mock_client
        
        mock_server = Mock()
        mock_fastmcp.from_openapi.return_value = mock_server
        
        create_and_run_mcp_server(
            "test.yml",
            auth_type="basic",
            credentials=("user", "pass")
        )
        
        # Verify auth handler was created
        mock_auth_handler.assert_called_once_with("basic", ("user", "pass"))
        mock_auth_instance.get_auth.assert_called_once()
        
        # Verify client was created with auth
        mock_httpx.AsyncClient.assert_called_once_with(base_url=None, auth=mock_auth)

    @patch('src.openapi_mcp_gen.server.FastMCP')
    @patch('src.openapi_mcp_gen.server.httpx')
    @patch('src.openapi_mcp_gen.server.load_openapi_spec')
    def test_create_and_run_mcp_server_with_base_url(self, mock_load_spec, mock_httpx, mock_fastmcp):
        """Test MCP server creation with base URL."""
        mock_spec = {"openapi": "3.0.0", "info": {"title": "Test"}}
        mock_load_spec.return_value = mock_spec
        
        mock_client = Mock()
        mock_httpx.AsyncClient.return_value = mock_client
        
        mock_server = Mock()
        mock_fastmcp.from_openapi.return_value = mock_server
        
        base_url = "https://api.example.com"
        create_and_run_mcp_server("test.yml", base_url=base_url)
        
        # Verify client was created with base_url
        mock_httpx.AsyncClient.assert_called_once_with(base_url=base_url, auth=None)

    @patch('src.openapi_mcp_gen.server.FastMCP')
    @patch('src.openapi_mcp_gen.server.httpx')
    @patch('src.openapi_mcp_gen.server.load_openapi_spec')
    def test_create_and_run_mcp_server_custom_params(self, mock_load_spec, mock_httpx, mock_fastmcp):
        """Test MCP server creation with custom parameters."""
        mock_spec = {"openapi": "3.0.0", "info": {"title": "Test"}}
        mock_load_spec.return_value = mock_spec
        
        mock_client = Mock()
        mock_httpx.AsyncClient.return_value = mock_client
        
        mock_server = Mock()
        mock_fastmcp.from_openapi.return_value = mock_server
        
        create_and_run_mcp_server(
            "test.yml",
            host="127.0.0.1",
            port=9000,
            name="Custom Server"
        )
        
        # Verify MCP server was created with custom name
        mock_fastmcp.from_openapi.assert_called_once_with(
            openapi_spec=mock_spec,
            client=mock_client,
            name="Custom Server"
        )
        
        # Verify server was started with custom host and port
        mock_server.run.assert_called_once_with(transport="http", host="127.0.0.1", port=9000)
