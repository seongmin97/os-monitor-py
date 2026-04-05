import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import apps.metrics.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sysdash.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(apps.metrics.routing.websocket_urlpatterns)
        ),
    }
)
