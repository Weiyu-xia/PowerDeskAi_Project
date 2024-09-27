from django.http import JsonResponse, StreamingHttpResponse
import json
from .client import Call_Dawatt, reset_conversation_id
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout
from django.views import View
import requests


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
        user_input = body_data.get('user_input', '')  # 获取用户输入
        print(user_input)

        response = StreamingHttpResponse(Call_Dawatt(user_input), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response


# 添加一个新的视图来处理情绪识别
def emotion_analysis(request):
    """
    处理情绪识别API调用并返回情绪标签。
    """
    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    chat_history = body_data.get('chat_history', [])

    # 获取用户输入的最后一句话
    user_last_sentence = chat_history[-1]['content'] if chat_history else ""

    # 调用情绪识别API
    api_url = "http://127.0.0.1:5000/api/emotion"  # 假设情绪识别API在这个端口
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    body = {"text": user_last_sentence}

    try:
        # 调用情绪识别API并获取结果
        emotion_response = requests.post(api_url, json=body, headers=headers)
        emotion_data = emotion_response.json()
        emotion_label = emotion_data.get('emotion_label', "未知")

        # 返回情绪识别结果
        return JsonResponse({'emotion_label': emotion_label})

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)})


# 新的视图函数用于重置 conversation_id
def new_conversation(request):
    reset_conversation_id()  # 调用重置方法
    return JsonResponse({'message': 'conversation reset'})