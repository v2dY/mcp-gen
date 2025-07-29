# OpenAPI to MCP Generator Makefile
# Using uv as package manager

.PHONY: run
# Run targets
run: 
	@echo "🚀 Running OpenAPI to MCP generator..."
	uv run openapi-to-mcp 
example: 
	@echo "🌟 Running example OpenAPI to MCP conversion..."
	uv run openapi-to-mcp --path examples/openapi.yaml --host 0.0.0.0 --port 8000 --server-name "Example MCP Server"