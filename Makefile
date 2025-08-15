# OpenAPI to MCP Generator Makefile
# Using uv as package manager

# Docker configuration
DOCKER_IMAGE_NAME ?= ghcr.io/v2dy/mcp-gen
DOCKER_TAG ?= latest
DOCKER_IMAGE = $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)
EXAMPLE_OPTS = --auth-type "api_key" --api-key-name "X-API-Key" --api-key-location "header" --api-key-value "${API_KEY}" --path "https://api.openaq.org/openapi.json" --host 0.0.0.0 --port 8000 --server-name "Example MCP Server" --base-url "https://api.openaq.org"
KIND_CLUSTER_NAME ?= kagent

.PHONY: run test test-coverage
# Run targets
run: 
	@echo "🚀 Running OpenAPI to MCP generator..."
	uv run openapi-to-mcp 

example: 
	@echo "🌟 Running example OpenAPI to MCP conversion..."
	uv run openapi-to-mcp generate $(EXAMPLE_OPTS)
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

# Docker targets
docker-build:
	@echo "🐳 Building Docker image $(DOCKER_IMAGE)..."
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	@echo "🐳 Running Docker container $(DOCKER_IMAGE)..."
	docker run --rm -it $(DOCKER_IMAGE)

docker-run-example:
	@echo "🐳 Running Docker example with mounted volume..."
	docker run --rm -it -p 8000:8000 -v $(PWD):/workspace:ro $(DOCKER_IMAGE) generate $(EXAMPLE_OPTS)

docker-load-kind:
	@echo "📦 Loading Docker image into kind cluster..."
	kind load docker-image $(DOCKER_IMAGE) --name ${KIND_CLUSTER_NAME}

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
	@echo "  run-inspector    - Run MCP inspector"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run Docker container"
	@echo "  docker-run-example - Run Docker container with example"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "📦 Docker variables (can be overridden):"
	@echo "  DOCKER_IMAGE_NAME - Docker image name (default: openapi-mcp-gen)"
	@echo "  DOCKER_TAG        - Docker image tag (default: latest)"
	@echo "  Example: make docker-build DOCKER_TAG=v1.0.0"