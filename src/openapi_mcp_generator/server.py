import json
import yaml  
import httpx
from fastmcp import FastMCP

def load_openapi_spec(file_path):
    """Load OpenAPI spec by trying YAML first, then JSON."""
    with open(file_path, 'r') as f:
        try:
            return yaml.safe_load(f)  # Try loading as YAML
        except yaml.YAMLError:
            f.seek(0)  # Reset file pointer
            return json.load(f)  # Fallback to JSON

def create_and_run_mcp_server(openapi_spec_path, host="0.0.0.0", port=8000, name="Generated MCP Server", base_url=None):
    """Create and run a FastMCP server from an OpenAPI spec file."""
    openapi_spec = load_openapi_spec(openapi_spec_path)

    # Create client with base_url if provided
    if base_url:
        client = httpx.AsyncClient(base_url=base_url)
    else:
        client = httpx.AsyncClient()

    mcp_server = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        client=client,
        name=name
    )

    mcp_server.run(transport="http", host=host, port=port)
