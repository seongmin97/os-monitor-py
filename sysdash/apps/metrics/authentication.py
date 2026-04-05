from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.servers.models import Server


class ApiKeyAuthentication(BaseAuthentication):
    """Authenticates agent requests using the Server's API key."""

    def authenticate(self, request):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None
        try:
            server = Server.objects.get(api_key=api_key, is_active=True)
        except (Server.DoesNotExist, Exception):
            raise AuthenticationFailed("Invalid or inactive API key.")
        return (server, None)
