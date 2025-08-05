# OpenAPI MCP Generator

A powerful tool to generate [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) servers from OpenAPI specifications with comprehensive authentication support.

## 🚀 Features

- **OpenAPI 3.0+ Support**: Generate MCP servers from YAML or JSON OpenAPI specifications
- **File & URL Support**: Load specifications from local files or remote URLs
- **Authentication Strategies**: Full support for OpenAPI security schemes:
  - 🔐 **Basic Authentication** - Username/password authentication
  - 🎫 **Bearer Token Authentication** - Authorization header with tokens
  - 🔑 **API Key Authentication** - Header or query parameter API keys
  - 🔒 **OAuth2 Client Credentials** - Automatic token management
- **CLI Interface**: Intuitive command-line interface with comprehensive validation
- **Configurable Server**: Customizable host, port, and server settings
- **Type Safety**: Full type hints and validation throughout
- **Comprehensive Testing**: 62 tests covering all authentication scenarios and functionality

## 📦 Installation

### Using pip
```bash
pip install openapi-mcp-gen
```

### Using uv (recommended for development)
```bash
uv add openapi-mcp-gen
```

### Using Docker
```bash
# Pull the latest image
docker pull ghcr.io/v2dy/mcp-gen:latest

# Run with help
docker run --rm ghcr.io/v2dy/mcp-gen:latest --help

# Run with your OpenAPI spec
docker run --rm -v $(pwd):/workspace:ro ghcr.io/v2dy/mcp-gen:latest generate \
  --path /workspace/your-openapi.yaml \
  --host 0.0.0.0 \
  --port 3000
```

Available Docker tags:
- `latest` - Latest stable release
- `v1.0.0` - Specific version tags
- `main` - Latest from main branch

## 🎯 Usage

### Quick Start
```bash
# Basic usage without authentication (local file)
openapi-to-mcp generate --path openapi.yml

# Basic usage with remote URL
openapi-to-mcp generate --path https://api.example.com/openapi.json

# With custom server settings
openapi-to-mcp generate --path openapi.yml --host 127.0.0.1 --port 8080 --server-name "My API Server"

# With base URL override
openapi-to-mcp generate --path openapi.yml --base-url "https://api.example.com"
```

### 🔐 Authentication Examples

#### Basic Authentication
```bash
openapi-to-mcp generate \
  --path openapi.yml \
  --auth-type basic \
  --basic-username myuser \
  --basic-password mypassword
```

#### Bearer Token Authentication
```bash
openapi-to-mcp generate \
  --path openapi.yml \
  --auth-type bearer \
  --bearer-token "your-jwt-token-here"
```

#### API Key in Header
```bash
openapi-to-mcp generate \
  --path openapi.yml \
  --auth-type api_key \
  --api-key-location header \
  --api-key-name "X-API-Key" \
  --api-key-value "your-secret-key"
```

#### API Key in Query Parameter
```bash
openapi-to-mcp generate \
  --path openapi.yml \
  --auth-type api_key \
  --api-key-location query \
  --api-key-name "apikey" \
  --api-key-value "your-secret-key"
```

#### OAuth2 Client Credentials
```bash
openapi-to-mcp generate \
  --path openapi.yml \
  --auth-type oauth2 \
  --oauth-token-url "https://auth.example.com/oauth/token" \
  --oauth-client-id "your-client-id" \
  --oauth-client-secret "your-client-secret" \
  --oauth-scope "read write"
```

### 📋 CLI Options

| Option | Description | Required |
|--------|-------------|----------|
| `--path`, `-f` | Path to OpenAPI specification file (YAML/JSON) or URL | ✅ |
| `--base-url` | Override base URL for API calls | ❌ |
| `--host` | Host to run MCP server on (default: 0.0.0.0) | ❌ |
| `--port` | Port to run MCP server on (default: 3000) | ❌ |
| `--server-name` | Name of the MCP server (default: "MCP Server") | ❌ |
| `--auth-type` | Authentication type: `basic`, `bearer`, `api_key`, `oauth2` | ❌ |

#### Authentication-specific options:
- **Basic**: `--basic-username`, `--basic-password`
- **Bearer**: `--bearer-token`
- **API Key**: `--api-key-location`, `--api-key-name`, `--api-key-value`
- **OAuth2**: `--oauth-token-url`, `--oauth-client-id`, `--oauth-client-secret`, `--oauth-scope`

### 🎯 Real-world Example

Using the OpenAQ API directly from their public URL:
```bash
# Run the OpenAQ API MCP server without authentication
openapi-to-mcp generate \
  --path "https://api.openaq.org/openapi.json" \
  --base-url "https://api.openaq.org" \
  --server-name "OpenAQ API Server" \
  --host 127.0.0.1 \
  --port 8080

# Or use the convenience make target
make example
```

## 🐳 Docker Usage

### Quick Start with Docker
```bash
# Basic usage with local file
docker run --rm -v $(pwd):/workspace:ro ghcr.io/v2dy/mcp-gen:latest generate \
  --path /workspace/openapi.yaml \
  --host 0.0.0.0 \
  --port 3000

# Basic usage with remote URL (no volume needed)
docker run --rm ghcr.io/v2dy/mcp-gen:latest generate \
  --path https://api.example.com/openapi.json \
  --host 0.0.0.0 \
  --port 3000
```

### Authentication Examples with Docker
```bash
# API Key authentication
docker run --rm -v $(pwd):/workspace:ro \
  -e API_KEY=your-secret-key \
  ghcr.io/v2dy/mcp-gen:latest generate \
  --path /workspace/openapi.yaml \
  --auth-type api_key \
  --api-key-name "X-API-Key" \
  --api-key-location header \
  --api-key-value "${API_KEY}"

# Basic authentication
docker run --rm -v $(pwd):/workspace:ro \
  ghcr.io/v2dy/mcp-gen:latest generate \
  --path /workspace/openapi.yaml \
  --auth-type basic \
  --basic-username myuser \
  --basic-password mypassword
```

### Available Docker Tags
- `ghcr.io/v2dy/mcp-gen:latest` - Latest release
- `ghcr.io/v2dy/mcp-gen:v1.0.0` - Specific version tags

See [DOCKER.md](DOCKER.md) for comprehensive Docker documentation.

## 🛠️ Development

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd mcp_generator

# Install with development dependencies
uv install

# Or using pip
pip install -e ".[dev]"
```

### 🧪 Testing

We have comprehensive test coverage with 62 tests covering all features:

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage
```

### 🛠️ Available Make Targets

```bash
# Development
make install           # Install dependencies  
make format           # Format code with black and isort
make lint             # Run type checking with mypy
make clean            # Clean up temporary files

# Running
make run              # Run the CLI tool
make example          # Run with example OpenAPI spec

# Testing
make test             # Run all tests
make test-coverage    # Run tests with coverage report

# Docker
make docker-build     # Build Docker image
make docker-run       # Run Docker container
make docker-run-example # Run Docker container with example

# Utilities
make run-inspector    # Run MCP inspector
make help             # Show all available targets
```

### 🎨 Code Quality

```bash
# Format code
make format

# Type checking
make lint
```

### 📁 Project Structure

```
src/openapi_mcp_gen/
├── __init__.py          # Package initialization
├── cli.py              # CLI interface with authentication options
├── server.py           # FastMCP server creation and management
└── auth.py             # Authentication handlers for all strategies

tests/
├── test_auth.py        # Authentication handler tests (12 tests)
├── test_cli.py         # CLI functionality tests (14 tests)
├── test_server.py      # Server creation tests (7 tests)
├── test_integration.py # End-to-end integration tests (6 tests)
└── test_openapi_spec_handler.py # OpenAPI spec handler tests (23 tests)

examples/
├── openapi.yml         # Open-Meteo weather API example
└── openapi.json        # OpenAQ air quality API example
```

## 🔧 OpenAPI Security Scheme Support

This tool supports all standard OpenAPI 3.0+ security schemes:

```yaml
# In your OpenAPI spec
components:
  securitySchemes:
    # Basic Authentication
    BasicAuth:
      type: http
      scheme: basic
    
    # Bearer Token
    BearerAuth:
      type: http
      scheme: bearer
    
    # API Key in Header
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
    
    # API Key in Query
    QueryKeyAuth:
      type: apiKey
      in: query
      name: api_key
    
    # OAuth2 Client Credentials
    OAuth2:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.com/token
          scopes:
            read: Read access
            write: Write access
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run the test suite: `make test`
5. Format your code: `make format`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - The underlying MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol this tool implements
- [OpenAPI Initiative](https://www.openapis.org/) - For the API specification standard
