from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class UserInfo(AbstractUser):
    """
    用户信息
    """
    desc = models.CharField(max_length=30, null=True, blank=True,
                            default='这个人很懒，什么都没留下',verbose_name='个人介绍')
    # django多对多关系是对称的，即你是我的朋友，那我也是你的朋友。symmetrical=False 取消对称
    friend = models.ManyToManyField('self', verbose_name='好友',symmetrical=False)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class ChatGroup(models.Model):
    """
    聊天房间
    """
    name = models.CharField(max_length=30, unique=True, verbose_name='房间名')
    desc = models.CharField(max_length=60, default='这个群主很懒，什么也没写', verbose_name='房间简介')
    create_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(UserInfo, verbose_name='房间创建者',
                              related_name='own_group', on_delete=models.CASCADE)
    members = models.ManyToManyField(UserInfo, verbose_name='成员',
                                related_name='join_groups')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '聊天房间'
        verbose_name_plural = verbose_name


class ChatMessage(models.Model):
    """
    聊天消息
    """
    sender = models.ForeignKey(UserInfo, related_name='send_msg', on_delete=models.CASCADE,
                               verbose_name='发送者')
    rece_id = models.IntegerField(verbose_name='接受者id')
    msg_type = models.CharField(choices=(('group', '组消息'), ('single', '个人消息')),
                                max_length=6, verbose_name='消息类型', default='group')
    message = models.CharField(max_length=128, verbose_name='消息')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = verbose_name

    @property
    def send_time(self):
        return self.create_time.strftime("%m-%d %H:%M:%S")
