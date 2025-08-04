"""Command-line interface for the OpenAPI to MCP generator."""

import os
import yaml
from pathlib import Path
from typing import Optional
import importlib.metadata

import click

from .server import create_and_run_mcp_server
from .auth import AuthHandler

def get_version():
    """Get version from package metadata."""
    try:
        return importlib.metadata.version("openapi-mcp-generator")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"

@click.group()
@click.version_option(version=get_version())
def cli():
    """OpenAPI to MCP Generator.
    
    Generate MCP (Model Context Protocol) servers from OpenAPI specifications.
    """
    pass


@cli.command()
@click.option(
    "--path", "-f",
    required=True,
    help="Path to OpenAPI specification file JSON or YAML"
)
@click.option(
    "--base-url",
    help="Override base URL for API calls"
)
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to run the MCP server on"
)
@click.option(
    "--port",
    default=3000,
    type=int,
    help="Port to run the MCP server on"
)
@click.option(
    "--server-name",
    default="MCP Server",
    help="Name of the MCP server"
)
@click.option(
    "--auth-type",
    type=click.Choice(["basic", "bearer", "api_key", "oauth2"], case_sensitive=False),
    help="Authentication type (basic, bearer, api_key, oauth2)"
)
@click.option(
    "--basic-username",
    help="Username for basic authentication"
)
@click.option(
    "--basic-password",
    help="Password for basic authentication"
)
@click.option(
    "--bearer-token",
    help="Token for bearer authentication"
)
@click.option(
    "--api-key-location",
    type=click.Choice(["header", "query"], case_sensitive=False),
    help="Location for API key (header or query)"
)
@click.option(
    "--api-key-name",
    help="Name of the API key"
)
@click.option(
    "--api-key-value",
    help="Value of the API key"
)
@click.option(
    "--oauth-token-url",
    help="Token URL for OAuth2 authentication"
)
@click.option(
    "--oauth-client-id",
    help="Client ID for OAuth2 authentication"
)
@click.option(
    "--oauth-client-secret",
    help="Client Secret for OAuth2 authentication"
)
@click.option(
    "--oauth-scope",
    help="Scope for OAuth2 authentication"
)
def generate(
    path: str,
    base_url: Optional[str] = None,
    host: str = "0.0.0.0",
    port: int = 3000,
    server_name: str = "MCP Server",
    auth_type: Optional[str] = None,
    basic_username: Optional[str] = None,
    basic_password: Optional[str] = None,
    bearer_token: Optional[str] = None,
    api_key_location: Optional[str] = None,
    api_key_name: Optional[str] = None,
    api_key_value: Optional[str] = None,
    oauth_token_url: Optional[str] = None,
    oauth_client_id: Optional[str] = None,
    oauth_client_secret: Optional[str] = None,
    oauth_scope: Optional[str] = None
):
    """Generate an MCP server from an OpenAPI specification."""
    
    try:
        input_path = Path(path)
        if not input_path.exists():
            click.echo(f"Error: Input file not found: {path}", err=True)
            return
        
        click.echo(f"Starting MCP server from: {path}")
        click.echo(f"Server will run on: {host}:{port}")
        if base_url:
            click.echo(f"Using base URL: {base_url}")
        if auth_type:
            click.echo(f"Using authentication type: {auth_type}")
        
        # Validate authentication options
        credentials = None
        if auth_type == "basic":
            if not basic_username or not basic_password:
                raise click.ClickException("Basic authentication requires both username and password.")
            credentials = (basic_username, basic_password)
        elif auth_type == "bearer":
            if not bearer_token:
                raise click.ClickException("Bearer authentication requires a token.")
            credentials = bearer_token
        elif auth_type == "api_key":
            if not api_key_location or not api_key_name or not api_key_value:
                raise click.ClickException("API key authentication requires location, name, and value.")
            credentials = (api_key_location, api_key_name, api_key_value)
        elif auth_type == "oauth2":
            if not oauth_token_url or not oauth_client_id or not oauth_client_secret or not oauth_scope:
                raise click.ClickException("OAuth2 authentication requires token URL, client ID, client secret, and scope.")
            credentials = (oauth_token_url, oauth_client_id, oauth_client_secret, oauth_scope)

        # Prepare arguments for the server
        server_kwargs = {
            "openapi_spec_path": input_path,  # Pass the file path, not the loaded spec
            "host": host,
            "port": port,
            "name": server_name,
            "auth_type": auth_type,
            "credentials": credentials
        }
        
        # Only add base_url if it's provided
        if base_url:
            server_kwargs["base_url"] = base_url
            
        create_and_run_mcp_server(**server_kwargs)
    except Exception as e:
        click.echo(f"Error running MCP server: {e}", err=True)
        raise click.ClickException(str(e))

def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
