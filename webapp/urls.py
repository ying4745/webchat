#!/usr/bin/python3
# DateTime: 2018/12/27 17:10

from django.urls import path

from webapp.views import RegisterView, IndexView, UserEditView, \
    LogoutView, AddHandleView, CreateGroupView, ChatGroupView, ChatFriendView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # 注册
    path('userinfo/edit/', UserEditView.as_view(), name='useredit'),  # 修改个人简介
    path('logout/', LogoutView.as_view(), name='logout'),  # 退出
    path('add/handle/', AddHandleView.as_view(), name='add_handle'),  # 添加好友和房间
    path('create/group/', CreateGroupView.as_view(), name='create_group'),  # 创建聊天房间

    path('chat/group/<int:g_id>/', ChatGroupView.as_view(), name='chat_group'),  # 聊天房间页面
    path('chat/friend/<int:f_id>/', ChatFriendView.as_view(), name='chat_friend'),  # 好友聊天页面
    # path('chat/friend/', views.chat_friend, name='chat_friend'),
    path('', IndexView.as_view(), name='index'),

    ]
