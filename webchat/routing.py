#!/usr/bin/python3
# DateTime: 2018/12/27 17:00

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import webapp.routing

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            webapp.routing.websocket_urlpatterns
            )
        ),
    })
