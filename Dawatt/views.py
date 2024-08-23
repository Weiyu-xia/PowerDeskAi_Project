from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.views.generic import View
from django.http import JsonResponse
import json

from .client import Call_Dawatt, Print_Dawatt


# 登录界面
class LoginPage(TemplateView):
    template_name = 'Dawatt/login.html'


# 大瓦特智能客服聊天界面
class DawattView(TemplateView):
    template_name = 'Dawatt/welcome.html'

    def post(self, request, *args, **kwargs):
        # 将获取的json转化为字典形式
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        chat_history = body_data.get('chat_history', [])

        reply = Call_Dawatt(chat_history)
        chat_history.append({'role': 'assistant', 'content': reply})  # 将大模型的回复添加到聊天记录
        Print_Dawatt(chat_history)

        # 返回 JSON 响应，包括生成的回复和格式化的聊天记录
        return JsonResponse({'reply': reply})
