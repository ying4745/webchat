#!/usr/bin/python3
# DateTime: 2018/12/27 19:32

import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django_redis import get_redis_connection

from webapp.models import ChatMessage


class ChatGroupConsumer(WebsocketConsumer):
    """聊天房间消费者"""

    def send_msg(self, msg, msg_type='msg'):
        """ 消息发送到群组里 """
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_id,
            {
                'type': 'chat_message',
                'message': msg,
                'msg_type': msg_type
                }
            )

    def connect(self):
        self.g_id = self.scope['url_route']['kwargs']['g_id']
        self.room_group_id = 'chat_%s' % self.g_id
        self.user_name = self.scope['user'].username

        msg_data = self.user_name + ' 进入了房间'

        # 加入房间组
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_id,
            self.channel_name
            )

        self.send_msg(msg_data, 'hint')

        self.accept()

    def disconnect(self, code):
        # 离开房间组
        msg_data = self.user_name + ' 离开了房间'

        self.send_msg(msg_data, 'hint')

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_id,
            self.channel_name
            )


    # 接受来自websocket的消息
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        msg_data = text_data_json['message']

        msg_obj = ChatMessage.objects.create(sender=self.scope['user'],
                                             rece_id=self.g_id,
                                             msg_type='group',
                                             message=msg_data)
        send_time = msg_obj.send_time

        msg = {
            "user_name": self.user_name,
            "send_time": send_time,
            "msg_data": msg_data
            }

        # 发送消息给房间组
        self.send_msg(msg)

    # 接受来自群组的消息，发送给各自的websocket
    def chat_message(self, event):
        message = event['message']
        msg_type = event['msg_type']

        # 发送消息给websocket
        self.send(text_data=json.dumps({
            'message': message,
            'msg_type': msg_type
            }))


class ChatFriendConsumer(WebsocketConsumer):
    """好友聊天消费者"""

    def connect(self):
        self.f_id = self.scope['url_route']['kwargs']['f_id']
        self.user_name = self.scope['user'].username

        # 连接时将自己的通道名字存入redis中
        self.con = get_redis_connection("default")
        self.con.hset('channels_list', self.scope['user'].id, self.channel_name)

        self.accept()

    def disconnect(self, code):

        # 断开时 删除自己的通道名
        self.con.hdel('channels_list', self.scope['user'].id, self.channel_name)


    # 接受来自websocket的消息
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        msg_data = text_data_json['message']

        msg_obj = ChatMessage.objects.create(sender=self.scope['user'],
                                             rece_id=self.f_id,
                                             msg_type='single',
                                             message=msg_data)
        send_time = msg_obj.send_time
        msg = {
            "user_id": self.scope['user'].id,
            "user_name": self.user_name,
            "send_time": send_time,
            "msg_data": msg_data
            }

        # 将消息发送给自己的通道
        async_to_sync(self.channel_layer.send)(
            self.channel_name,
            {
                'type': 'chat_f_message',
                'message': msg
                }
            )

        # 如果对方在连接中，那直接发送给对方的通道中
        rece_channel_name = self.con.hget('channels_list', self.f_id)
        if rece_channel_name:
            rece_channel_name = rece_channel_name.decode('utf8')
            async_to_sync(self.channel_layer.send)(
                rece_channel_name,
                {
                    'type': 'chat_f_message',
                    'message': msg
                    }
                )

    # 接受来自通道的消息，发送给各自的websocket
    def chat_f_message(self, event):
        message = event['message']

        # 发送消息给websocket
        self.send(text_data=json.dumps({
            'message': message,
            }))