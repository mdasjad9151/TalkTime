

# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from chat.routing import websocket_urlpatterns

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TalkTime.settings')

# django.setup()  # Ensure Django is initialized before importing anything

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(  # Wrap WebSocket with auth middleware
#         URLRouter(websocket_urlpatterns)
#     ),
# })


import os
import django
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TalkTime.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # Adds user to self.scope["user"]
        SessionMiddlewareStack(       # Ensures session-based authentication
            URLRouter(websocket_urlpatterns)
        )
    ),
})

