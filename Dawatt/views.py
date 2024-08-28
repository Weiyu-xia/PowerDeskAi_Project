from django.db import models
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import JsonResponse
import json
from django.utils.html import escape
from django.db.models import Q
from .client import Call_Dawatt_history, Print_Dawatt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from .models import User_infomation


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

    #先放在这里
    sql_generate = "从以下SQL语句中选择："

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        chat_history = body_data.get('chat_history', [])

        # Fetch the latest user message
        user_message = chat_history[-1]['content']

        # Check if the user is querying electricity fees
        if "电费" in user_message:
            # Generate a prompt for the verification process
            prompt = f"用户输入了与电费相关的问题。请要求用户提供<预留手机号码/身份证号码/用户编号>。"
            user_message = user_message + " " + prompt
            chat_history.append({'role': 'user', 'content': user_message})

            # Call the model to generate a response
            reply = Call_Dawatt_history(chat_history)
            chat_history.append({'role': 'assistant', 'content': reply})
            # Determine which field to verify first based on model response
            if any(keyword in chat_history[-1]['content'] for keyword in ["手机号码", "身份证号码", "用户编号"]):
                # Simulate asking for user input
                # prompt = "提取用户发送的相关号码，生成相应的SQL语句，" + sql_generate + "此处的用户输入：" + chat_history[-1]['content']
                chat_history.append({'role': 'user', 'content': prompt})
                reply = Call_Dawatt_history(chat_history)
                chat_history.append({'role': 'assistant', 'content': reply})

                # Example of checking the user's input against the database
                user_input = chat_history[-1]['content']
                user = User_infomation.objects.filter(
                    Q(phone_number=user_input) |
                    Q(id_number=user_input) |
                    Q(user_code=user_input)
                ).first()

                if user:
                    # Continue with the verification process
                    prompt = f"验证成功，请输入以下任意一项资料完成身份验证: " \
                             f"身份证号、用户编号的后4位或缴费账号的后4位。"
                    chat_history.append({'role': 'system', 'content': prompt})
                    reply = Call_Dawatt_history(chat_history)
                else:
                    reply = "未找到用户信息，请重新输入。"
                    chat_history.append({'role': 'assistant', 'content': reply})
            else:
                reply = Call_Dawatt_history(chat_history)
        else:
            # Handle normal conversation or other queries
            reply = Call_Dawatt_history(chat_history)

        reply = escape(reply).replace('\n', '<br>')
        chat_history.append({'role': 'assistant', 'content': reply})
        Print_Dawatt(chat_history)

        return JsonResponse({'reply': reply})
