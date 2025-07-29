"""Command-line interface for the OpenAPI to MCP generator."""

import os
import yaml
from pathlib import Path
from typing import Optional

import click

from .server import create_and_run_mcp_server

@click.group()
@click.version_option(version="0.1.0")
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


def generate(
    path: str,
    base_url: Optional[str] = None,
    host: str = "0.0.0.0",
    port: int = 3000,
    server_name: str = "MCP Server"
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
        
        # Prepare arguments for the server
        server_kwargs = {
            "openapi_spec_path": input_path,  # Pass the file path, not the loaded spec
            "host": host,
            "port": port,
            "name": server_name
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
