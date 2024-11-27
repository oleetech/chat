import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# HTTP এবং WebSocket প্রোটোকলের জন্য কনফিগারেশন
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # HTTP রিকোয়েস্ট হ্যান্ডল
        "websocket": AuthMiddlewareStack(  # WebSocket প্রোটোকলে AuthMiddlewareStack যুক্ত করা হয়েছে
            URLRouter(websocket_urlpatterns)  # WebSocket URL প্যাটার্ন হ্যান্ডল
        ),
    }
)
