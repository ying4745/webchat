#!/usr/bin/python3
# DateTime: 2018/12/28 10:44
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20,
                               min_length=4,
                               label='用户名',
                               label_suffix='',
                               widget=forms.widgets.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': '用户名4-20个字符'}),
                               error_messages={
                                   'required': '用户名不能为空',
                                   'max_length': '用户名长度不能大于20个字符',
                                   'min_length': '用户名长度不能小于4个字符'
                                   })
    password = forms.CharField(min_length=6,
                               label='密码',
                               label_suffix='',
                               widget=forms.widgets.PasswordInput(
                                   attrs={'class': 'form-control',
                                          'placeholder': '密码不能少于6位'}),
                               error_messages={
                                   'required': '密码不能为空',
                                   'min_length': '密码长度不能小于6个字符',
                                   })


class RegisterForm(LoginForm):
    re_password = forms.CharField(min_length=6,
                                  label='确认密码',
                                  label_suffix='',
                                  widget=forms.widgets.PasswordInput(
                                      attrs={'class': 'form-control',
                                             'placeholder': '再输一次密码'}),
                                  error_messages={
                                      'required': '密码不能为空',
                                      'min_length': '密码长度不能小于6个字符',
                                      })


class AddGroupForm(forms.Form):
    name = forms.CharField(max_length=30,
                           label='房间名字',
                           label_suffix='',
                           widget=forms.widgets.TextInput(
                               attrs={'class': 'form-control'}),
                           error_messages={
                               'required': '房间名字不能为空',
                               'max_length': '房间名字长度不能大于30个字符',
                               })
    desc = forms.CharField(max_length=60,
                           label='房间描述',
                           label_suffix='',
                           widget=forms.widgets.Textarea(
                               attrs={'class': 'form-control',
                                      'placeholder': '简单介绍一下房间主题'}),
                           error_messages={
                               'max_length': '房间描述长度不能大于60个字符',
                               })
