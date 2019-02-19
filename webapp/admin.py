from django.contrib import admin

from .models import UserInfo, ChatGroup, ChatMessage


admin.site.register(UserInfo)
admin.site.register(ChatGroup)
admin.site.register(ChatMessage)