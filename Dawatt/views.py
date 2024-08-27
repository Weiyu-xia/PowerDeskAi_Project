from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
import json
from django.utils.html import escape
from .client import Call_Dawatt, Print_Dawatt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View


# 登录界面
class LoginPage(TemplateView):
    template_name = 'Dawatt/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('DawattChat')  # 如果用户已登录，重定向到欢迎页面
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            # 进行身份验证
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # 如果用户存在且验证成功
                login(request, user)
                return redirect('DawattChat')  # 确保在urls.py中定义了'DawattChat' URL名称
            else:
                # 如果用户不存在或密码不匹配
                messages.error(request, '用户名或密码错误')
                return render(request, self.template_name)
        else:
            return render(request, self.template_name)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')  # 重定向到登录页面


# 大瓦特智能客服聊天界面
class DawattView(LoginRequiredMixin, TemplateView):
    template_name = 'Dawatt/DawattChat.html'

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
