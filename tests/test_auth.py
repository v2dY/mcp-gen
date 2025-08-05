from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.openapi_mcp_gen.auth import AuthHandler


class TestAuthHandler:
    """Test suite for AuthHandler class."""

    def test_init_no_auth(self):
        """Test initialization without authentication."""
        handler = AuthHandler()
        assert handler.auth_type is None
        assert handler.credentials is None

    def test_init_with_auth(self):
        """Test initialization with authentication."""
        handler = AuthHandler("basic", ("user", "pass"))
        assert handler.auth_type == "basic"
        assert handler.credentials == ("user", "pass")

    def test_get_auth_no_type(self):
        """Test get_auth returns None when no auth type is set."""
        handler = AuthHandler()
        assert handler.get_auth() is None

    def test_basic_auth(self):
        """Test basic authentication handler."""
        handler = AuthHandler("basic", ("testuser", "testpass"))
        auth = handler.get_auth()

        assert isinstance(auth, httpx.BasicAuth)
        # Test that the auth object was created correctly by checking its type
        # The actual username/password are private implementation details

    def test_bearer_auth(self):
        """Test bearer token authentication handler."""
        token = "test-bearer-token"
        handler = AuthHandler("bearer", token)
        auth = handler.get_auth()

        # Test the auth flow
        request = Mock()
        request.headers = {}

        auth_flow = auth.auth_flow(request)
        next(auth_flow)

        assert request.headers["Authorization"] == f"Bearer {token}"

    def test_api_key_header_auth(self):
        """Test API key authentication in header."""
        handler = AuthHandler("api_key", ("header", "X-API-Key", "test-key"))
        auth = handler.get_auth()

        # Test the auth flow
        request = Mock()
        request.headers = {}

        auth_flow = auth.auth_flow(request)
        next(auth_flow)

        assert request.headers["X-API-Key"] == "test-key"

    def test_api_key_query_auth(self):
        """Test API key authentication in query parameters."""
        handler = AuthHandler("api_key", ("query", "api_key", "test-key"))
        auth = handler.get_auth()

        # Mock URL and params
        mock_url = Mock()
        mock_url.params = {}
        mock_url.copy_with.return_value = mock_url

        request = Mock()
        request.url = mock_url
        request.headers = {}

        auth_flow = auth.auth_flow(request)
        next(auth_flow)

        # Verify copy_with was called with updated params
        mock_url.copy_with.assert_called_once_with(params={"api_key": "test-key"})

    @pytest.mark.asyncio
    async def test_oauth2_auth(self):
        """Test OAuth2 authentication."""
        token_url = "https://auth.example.com/token"
        client_id = "test-client"
        client_secret = "test-secret"
        scope = "read write"

        handler = AuthHandler("oauth2", (token_url, client_id, client_secret, scope))
        auth = handler.get_auth()

        # Mock the token response
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "oauth-token"}
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            request = Mock()
            request.headers = {}

            # Test async auth flow
            auth_flow = auth.async_auth_flow(request)
            await auth_flow.__anext__()

            assert request.headers["Authorization"] == "Bearer oauth-token"

    def test_invalid_auth_type(self):
        """Test that invalid auth type returns None."""
        handler = AuthHandler("invalid", ("test",))
        assert handler.get_auth() is None

    def test_basic_auth_missing_credentials(self):
        """Test basic auth with missing credentials raises error."""
        handler = AuthHandler("basic", ("user",))  # Missing password

        with pytest.raises(ValueError):
            handler.get_auth()

    def test_api_key_auth_missing_credentials(self):
        """Test API key auth with missing credentials raises error."""
        handler = AuthHandler("api_key", ("header", "key"))  # Missing value

        with pytest.raises(ValueError):
            handler.get_auth()

    def test_oauth2_auth_missing_credentials(self):
        """Test OAuth2 auth with missing credentials raises error."""
        handler = AuthHandler("oauth2", ("url", "client"))  # Missing secret and scope

        with pytest.raises(ValueError):
            handler.get_auth()
