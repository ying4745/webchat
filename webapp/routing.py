#!/usr/bin/python3
# DateTime: 2018/12/27 19:36

from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/chat/group/<g_id>/', consumers.ChatGroupConsumer),
    path('ws/chat/friend/<f_id>/', consumers.ChatFriendConsumer),
    ]
