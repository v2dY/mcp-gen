# OpenAPI to MCP Generator Makefile
# Using uv as package manager

.PHONY: run test test-coverage
# Run targets
run: 
	@echo "🚀 Running OpenAPI to MCP generator..."
	uv run openapi-to-mcp 

example: 
	@echo "🌟 Running example OpenAPI to MCP conversion..."
	uv run openapi-to-mcp generate --path examples/openapi.json --host 0.0.0.0 --port 8000 --server-name "Example MCP Server" --base-url "https://api.openaq.org" --auth-type "api_key" --api-key-name "X-API-Key" --api-key-location "header" --api-key-value ${API_KEY}

# Test targets
test:
	@echo "🧪 Running all tests..."
	uv run pytest tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage report..."
	uv run pytest tests/ --cov=src/openapi_mcp_gen --cov-report=html --cov-report=term

# Development targets
install:
	@echo "📦 Installing dependencies..."
	uv install

format:
	@echo "🎨 Formatting code..."
	uv run black src/ tests/
	uv run isort src/ tests/

lint:
	@echo "🔍 Linting code..."
	uv run mypy src/

clean:
	@echo "🧹 Cleaning up..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

run-inspector:
	@echo "🔍 Running inspector..."
	npx @modelcontextprotocol/inspector
help:
	@echo "📖 Available targets:"
	@echo "  run              - Run the OpenAPI to MCP generator CLI"
	@echo "  example          - Run with example OpenAPI spec"
	@echo "  test             - Run all tests"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  install          - Install dependencies"
	@echo "  format           - Format code with black and isort"
	@echo "  lint             - Run type checking with mypy"
	@echo "  clean            - Clean up temporary files"
	@echo "  help             - Show this help message"