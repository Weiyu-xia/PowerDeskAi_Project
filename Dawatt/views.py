from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
import json
from django.utils.html import escape
from .client import Call_Dawatt, Print_Dawatt
from .models import UserInfo  # 导入你创建的模型


# 登录界面
class LoginPage(TemplateView):
    template_name = 'Dawatt/login.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'GET':
            return render(request, 'Dawatt/login.html')
        uname = request.POST.get('user')
        pwd = request.POST.get('pwd')
        # 在数据库中查找用户
        try:
            user = UserInfo.objects.get(name=uname, pwd=pwd)
            # 如果找到用户，重定向到欢迎页面
            return redirect('DawattChat/')  # 确保在urls.py中定义了'welcome' URL名称
        except UserInfo.DoesNotExist:
            # 如果用户不存在或密码不匹配，返回登录页面并显示错误信息
            return render(request, self.template_name, {"error_message": "用户名或密码错误"})


# 大瓦特智能客服聊天界面
class DawattView(TemplateView):
    template_name = 'Dawatt/welcome.html'

    def post(self, request, *args, **kwargs):
        # 将获取的json转化为字典形式
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        chat_history = body_data.get('chat_history', [])

        reply = Call_Dawatt(chat_history)
        reply = escape(reply).replace('\n', '<br>')

        chat_history.append({'role': 'assistant', 'content': reply})  # 将大模型的回复添加到聊天记录
        Print_Dawatt(chat_history)

        # 返回 JSON 响应，包括生成的回复和格式化的聊天记录
        return JsonResponse({'reply': reply})
