from django.http import JsonResponse, StreamingHttpResponse
import json
from .client import Call_Dawatt, reset_conversation_id, generate_conversation_id
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
        conversation_id = body_data.get('conversation_id', None)  # 获取会话ID
        print(user_input)

        response = StreamingHttpResponse(Call_Dawatt(user_input, conversation_id), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response


class MessageHistoryView(View):
    """
    处理根据 conversation_id 获取历史聊天记录的请求。
    """
    def get(self, request, *args, **kwargs):
        # 从请求参数中获取必要的参数
        conversation_id = request.GET.get('conversation_id', None)
        user = request.GET.get('user', 'abc-123')  # 假设用户 ID 是 'abc-123'
        first_id = request.GET.get('first_id', None)
        limit = request.GET.get('limit', 20)

        # 检查 conversation_id 是否存在
        if not conversation_id:
            return JsonResponse({'error': 'conversation_id is required'}, status=400)

        # 构建 API 请求的 URL 和参数
        api_url = "https://api.dify.ai/v1/messages"
        headers = {
            'Authorization': 'Bearer app-UbvRHc53mtaKn740Ht5SU9aD',  # 替换为你的实际 API 密钥
            'Content-Type': 'application/json'
        }

        # 构建 API 请求的参数
        params = {
            'conversation_id': conversation_id,
            'user': user,
            'first_id': first_id,
            'limit': limit
        }

        try:
            # 向外部 API 发送 GET 请求获取聊天记录
            response = requests.get(api_url, headers=headers, params=params)

            # 如果请求成功，返回聊天记录数据
            if response.status_code == 200:
                data = response.json()  # 解析 JSON 响应
                return JsonResponse(data)

            # 请求失败的处理
            else:
                return JsonResponse({'error': 'Failed to fetch chat history', 'details': response.text}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            # 捕获请求异常并返回错误信息
            return JsonResponse({'error': str(e)}, status=500)



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
    reset_conversation_id()  # 重置当前的会话 ID
    new_conv_id = generate_conversation_id()  # 生成新的会话 ID
    return JsonResponse({'message': '会话已重置', 'conversation_id': new_conv_id})