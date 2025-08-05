from typing import Optional, Tuple, Union

import httpx


class AuthHandler:
    """Handles authentication based on OpenAPI security schemes."""

    def __init__(
        self,
        auth_type: Optional[str] = None,
        credentials: Optional[Union[str, Tuple]] = None,
    ):
        self.auth_type = auth_type
        self.credentials = credentials

    def get_auth(self):
        """Get the appropriate authentication handler based on auth_type."""
        if self.auth_type == "basic":
            if not self.credentials or len(self.credentials) != 2:
                raise ValueError("Basic authentication requires username and password")
            username, password = self.credentials
            return httpx.BasicAuth(username, password)
        elif self.auth_type == "bearer":
            if not self.credentials:
                raise ValueError("Bearer authentication requires a token")
            token = self.credentials
            return self._create_bearer_auth(token)
        elif self.auth_type == "api_key":
            if not self.credentials or len(self.credentials) != 3:
                raise ValueError(
                    "API key authentication requires location, name, and value"
                )
            location, key_name, key_value = self.credentials
            return self._create_api_key_auth(location, key_name, key_value)
        elif self.auth_type == "oauth2":
            if not self.credentials or len(self.credentials) != 4:
                raise ValueError(
                    "OAuth2 authentication requires token URL, client ID, client secret, and scope"
                )
            token_url, client_id, client_secret, scope = self.credentials
            return self._get_oauth2_auth(token_url, client_id, client_secret, scope)
        return None

    def _create_bearer_auth(self, token: str):
        """Create bearer token authentication."""

        class BearerAuth(httpx.Auth):
            def __init__(self, token: str):
                self.token = token

            def auth_flow(self, request):
                request.headers["Authorization"] = f"Bearer {self.token}"
                yield request

        return BearerAuth(token)

    def _create_api_key_auth(self, location: str, key_name: str, key_value: str):
        """Create API key authentication."""

        class APIKeyAuth(httpx.Auth):
            def __init__(self, location: str, key_name: str, key_value: str):
                self.location = location
                self.key_name = key_name
                self.key_value = key_value

            def auth_flow(self, request):
                if self.location == "header":
                    request.headers[self.key_name] = self.key_value
                elif self.location == "query":
                    params = dict(request.url.params)
                    params[self.key_name] = self.key_value
                    request.url = request.url.copy_with(params=params)
                yield request

        return APIKeyAuth(location, key_name, key_value)

    def _get_oauth2_auth(
        self, token_url: str, client_id: str, client_secret: str, scope: str
    ):
        """Create OAuth2 client credentials authentication."""

        class OAuth2Auth(httpx.Auth):
            def __init__(
                self, token_url: str, client_id: str, client_secret: str, scope: str
            ):
                self.token_url = token_url
                self.client_id = client_id
                self.client_secret = client_secret
                self.scope = scope
                self._token = None

            async def async_auth_flow(self, request):
                if not self._token:
                    await self._get_token()
                request.headers["Authorization"] = f"Bearer {self._token}"
                yield request

            def auth_flow(self, request):
                # For sync clients, we need to handle this differently
                # This is a simplified version - in practice, you'd want proper token management
                request.headers["Authorization"] = (
                    f"Bearer {self._token or 'token_placeholder'}"
                )
                yield request

            async def _get_token(self):
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.token_url,
                        data={
                            "grant_type": "client_credentials",
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "scope": self.scope,
                        },
                    )
                    response.raise_for_status()
                    token_data = response.json()
                    self._token = token_data.get("access_token")

        return OAuth2Auth(token_url, client_id, client_secret, scope)
