import json

from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.utils.safestring import mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin

from webapp.form import RegisterForm, LoginForm, AddGroupForm
from webapp.models import UserInfo, ChatGroup, ChatMessage


class RegisterView(View):
    """注册视图"""

    def get(self, request):
        reg_form = RegisterForm()
        return render(request, 'register.html', {'reg_form': reg_form})

    def post(self, request):
        reg_form = RegisterForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data.get('username')
            password = reg_form.cleaned_data.get('password')
            re_password = reg_form.cleaned_data.get('re_password')

            # 判断两次密码是否一致
            if password != re_password:
                reg_form.errors['re_password'] = ['两次密码不一致']
                return JsonResponse({'status': 3, 'msg': reg_form.errors})

            # 查找用户名是否存在
            try:
                user = UserInfo.objects.get(username=username)
            except UserInfo.DoesNotExist:
                user = None

            if user:
                reg_form.errors['username'] = ['用户名已存在']
                return JsonResponse({'status': 2, 'msg': reg_form.errors})

            user = UserInfo.objects.create_user(username, password=password)
            user.is_active = 0
            user.save()
            return JsonResponse({'status': 0, 'msg': ''})

        return JsonResponse({'status': 1, 'msg': reg_form.errors})


class IndexView(View):
    """主页、登录视图"""

    def get(self, request):
        login_form = LoginForm()
        chat_groups = ChatGroup.objects.annotate(group_member=Count('members__id')).order_by('-group_member')
        # 未实现在线人数统计，暂时移除
        # chat_groups = chat_groups.filter(members__is_active=1).annotate(member_online=Count('members'))
        return render(request, 'index.html', {'login_form': login_form,
                                              'chat_groups': chat_groups})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username', '')
            password = login_form.cleaned_data.get('password', '')
            try:
                user = UserInfo.objects.get(username=username)
            except:
                user = None

            if user is not None and user.check_password(password):
                user.is_active = 1
                user.save()
                login(request, user)
                return JsonResponse({'status': 0, 'msg': ''})
            else:
                login_form.errors['password'] = ['用户名或密码错误']
                return JsonResponse({'status': 2, 'msg': login_form.errors})

        return JsonResponse({'status': 1, 'msg': login_form.errors})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        user.is_active = 0
        user.save()
        logout(request)
        return redirect(reverse('index'))


class UserEditView(LoginRequiredMixin, View):
    """用户编辑个人简介"""

    def post(self, request):
        user = request.user
        desc_data = request.POST.get('desc')
        try:
            user.desc = desc_data
            user.save()
        except:
            return JsonResponse({'status': 1, 'msg': '长度超出限制'})
        return JsonResponse({'status': 0, 'msg': ''})


class AddHandleView(LoginRequiredMixin, View):
    """添加好友、房间"""

    def post(self, request):
        user = request.user
        data_type = request.POST.get('type')
        keyword = request.POST.get('keyword', '')
        if not keyword:
            return JsonResponse({'status': 3, 'msg': '请输入要添加的名字'})

        if data_type == 'friend':
            try:
                friend_obj = UserInfo.objects.get(username=keyword)
            except UserInfo.DoesNotExist:
                return JsonResponse({'status': 2, 'msg': '名字错误'})

            if user.friend.filter(username=keyword).exists():
                return JsonResponse({'status': 1, 'msg': '请勿重复添加'})

            user.friend.add(friend_obj)
            return JsonResponse({'status': 0, 'msg': '添加成功'})

        elif data_type == 'group':
            try:
                group_obj = ChatGroup.objects.get(name=keyword)
            except ChatGroup.DoesNotExist:
                return JsonResponse({'status': 2, 'msg': '名字错误'})
            if user.own_group.filter(name=keyword).exists():
                return JsonResponse({'status': 4, 'msg': '不能添加自己的房间'})
            if user.join_groups.filter(name=keyword).exists():
                return JsonResponse({'status': 1, 'msg': '请勿重复添加'})

            group_obj.members.add(user)
            return JsonResponse({'status': 0, 'msg': '添加成功'})
        return JsonResponse({'status': 5, 'msg': '参数出错，添加失败！'})


class CreateGroupView(LoginRequiredMixin, View):
    """创建房间"""

    def get(self, request):
        add_group_form = AddGroupForm()
        return render(request, 'add_group.html', {'add_group_form': add_group_form})

    def post(self, request):
        user = request.user
        add_group_form = AddGroupForm(request.POST)
        if add_group_form.is_valid():
            name = add_group_form.cleaned_data.get('name')
            desc = add_group_form.cleaned_data.get('desc')
            try:
                ChatGroup.objects.create(name=name, desc=desc, owner=user)
            except:
                add_group_form.errors['name'] = ['房间名已存在']
                return JsonResponse({'status': 2, 'msg': add_group_form.errors})

            return JsonResponse({'status': 0, 'msg': '创建成功'})

        return JsonResponse({'status': 1, 'msg': add_group_form.errors})


class ChatGroupView(LoginRequiredMixin, View):
    """进入聊天房间"""

    def get(self, request, g_id):
        u_id = request.user.id
        group_message = ChatMessage.objects.filter(rece_id=g_id,
                                                   msg_type='group')
        try:
            # 排序取最新的五条信息后，再倒回正常排序
            group_message = group_message.order_by('-create_time')[0:5][::-1]
        except:
            group_message = group_message.order_by('create_time').all()

        group = ChatGroup.objects.get(id=g_id)
        if group.owner_id != u_id and not group.members.filter(id=u_id).exists():
            group.members.add(u_id)

        return render(request, 'chat_group.html', {'group': group,
                                                   'group_message': group_message})

    def post(self, request, g_id):
        """退出房间处理函数"""
        user = request.user
        try:
            group = ChatGroup.objects.get(id=g_id)
        except ChatGroup.DoesNotExist:
            return JsonResponse({'status': 2, 'msg': '参数错误'})
        if group.owner == user:
            group.delete()
            return JsonResponse({'status': 0, 'msg': '你已解散该房间'})
        group.members.remove(user)
        return JsonResponse({'status': 0, 'msg': '已成功退出该房间'})


class ChatFriendView(LoginRequiredMixin, View):
    """ 好友聊天视图"""

    def get(self, request, f_id):
        friend_obj = UserInfo.objects.get(id=f_id)
        friend_data = ChatMessage.objects.filter(Q(msg_type='single'),
                                                 Q(rece_id=request.user.id,
                                                   sender=friend_obj, is_read=True)|Q(
                                                     rece_id=f_id, sender=request.user))
        friend_msg = ChatMessage.objects.filter(rece_id=request.user.id,
                                                sender=friend_obj,
                                                msg_type='single',
                                                is_read=False)
        # 立即查询一次数据库
        friend_history_msg = friend_data.order_by('-create_time')[0:10][::-1]
        friend_not_read = list(friend_msg.all())
        # 更新消息已读状态
        friend_msg.update(is_read=True)
        return render(request, 'chat_friend.html', {'friend': friend_obj,
                                                    'friend_history_msg': friend_history_msg,
                                                    'friend_not_read_msg': friend_not_read})

    def post(self, request, f_id):
        pass

