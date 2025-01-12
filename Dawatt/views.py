import re

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
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为你的实际 API 密钥
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


# 获取会话列表
class ConversationsListView(View):
    """
    处理获取当前用户的会话列表的请求。
    """
    def get(self, request, *args, **kwargs):
        # 获取用户标识
        user_id = request.GET.get('user', 'abc-123')  # 假设默认用户ID是'abc-123'
        last_id = request.GET.get('last_id', None)
        limit = request.GET.get('limit', 20)

        # 构建 API 请求的 URL 和参数
        api_url = "https://api.dify.ai/v1/conversations"
        headers = {
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为你的实际 API 密钥
            'Content-Type': 'application/json'
        }

        # 构建请求参数
        params = {
            'user': user_id,
            'last_id': last_id,
            'limit': limit
        }

        try:
            # 向外部 API 发送 GET 请求以获取会话列表
            response = requests.get(api_url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()  # 解析 JSON 响应
                return JsonResponse(data)  # 返回会话列表数据

            # 处理请求失败的情况
            else:
                return JsonResponse({'error': 'Failed to fetch conversation list', 'details': response.text}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            # 捕获请求异常并返回错误信息
            return JsonResponse({'error': str(e)}, status=500)


# 删除会话的视图
class DeleteConversationView(View):
    """
    处理根据 conversation_id 删除会话的请求。
    """
    def delete(self, request, conversation_id, *args, **kwargs):
        user_id = request.GET.get('user', 'abc-123')  # 假设默认用户ID是'abc-123'

        # 构建 API 请求的 URL
        api_url = f"https://api.dify.ai/v1/conversations/{conversation_id}"
        headers = {
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为你的实际 API 密钥
            'Content-Type': 'application/json'
        }
        body = {
            'user': user_id
        }

        try:
            # 发送 DELETE 请求
            response = requests.delete(api_url, headers=headers, json=body)

            # 检查响应状态
            if response.status_code == 200:
                return JsonResponse({'result': 'success'})
            else:
                return JsonResponse({'error': 'Failed to delete conversation', 'details': response.text}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)


# 重命名会话的视图
class RenameConversationView(View):
    """
    处理根据 conversation_id 重命名会话的请求。
    """
    def post(self, request, conversation_id, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        new_name = body_data.get('name', '').strip()  # 获取新的会话名称
        user_id = body_data.get('user', 'abc-123')  # 默认用户ID

        # 检查名称是否为空
        if not new_name:
            return JsonResponse({'error': 'Invalid name'}, status=400)

        # 构建 API 请求的 URL
        api_url = f"https://api.dify.ai/v1/conversations/{conversation_id}/name"
        headers = {
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为你的实际 API 密钥
            'Content-Type': 'application/json'
        }
        body = {
            'name': new_name,  # 手动输入的名称
            'auto_generate': False,  # 禁用自动生成
            'user': user_id
        }

        try:
            response = requests.post(api_url, headers=headers, json=body)
            print(f"API response: {response.status_code}, {response.text}")  # 打印 API 响应调试信息

            if response.status_code == 200:
                return JsonResponse({'result': 'success'})
            else:
                return JsonResponse({'error': 'Failed to rename conversation', 'details': response.text},
                                    status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)



class GenerateTicketView(View):
    """
    处理根据聊天记录生成工单的请求。
    """
    def post(self, request, *args, **kwargs):
        # 获取前端传来的聊天记录
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        chat_history = body_data.get('chat_history', [])

        # 准备API调用的请求数据
        api_url = "https://api.dify.ai/v1/chat-messages"
        headers = {
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为你的API密钥
            'Content-Type': 'application/json'
        }

        payload = {
            "query": chat_history,
            "inputs": {},  # 如果有额外的输入变量，可以在这里添加
            "response_mode": "blocking",  # 使用阻塞模式
            "user": "abc-123",  # 设置用户标识
            "conversation_id": None  # 可选，如果需要继续某个会话
        }

        try:
            # 向大模型发送POST请求
            response = requests.post(api_url, headers=headers, json=payload)

            # 检查请求是否成功
            if response.status_code == 200:
                response_data = response.json()
                ticket_summary = response_data.get("answer", "未生成工单摘要")

                # 通过正则表达式匹配并移除 ```html 和末尾的 ```
                clean_summary = re.sub(r'```html\s*|```', '', ticket_summary).strip()

                # 返回生成的工单摘要
                return JsonResponse({'summary': clean_summary})
            else:
                return JsonResponse({'error': 'Failed to generate ticket', 'details': response.text},
                                    status=response.status_code)

        except requests.exceptions.RequestException as e:
            # 捕获请求异常并返回错误信息
            return JsonResponse({'error': str(e)}, status=500)




# 添加一个新的视图来处理情绪识别
def emotion_analysis(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        chat_history = body_data.get('chat_history', [])
        # 获取用户输入的最后一句话
        user_last_sentence = chat_history[-1]['content'] if chat_history else ""

        # 调用情绪识别API
        api_url = "https://api.dify.ai/v1/chat-messages"

        headers = {
            'Authorization': 'Bearer app-SD8NAi3M51Gw15kdDOTXcqtC',  # 替换为你的API密钥
            'Content-Type': 'application/json'
        }

        payload = {
            "query": user_last_sentence,
            "inputs": {},  # 如果有额外的输入变量，可以在这里添加
            "response_mode": "blocking",  # 使用阻塞模式
            "user": "abc-123",  # 设置用户标识
            "conversation_id": None  # 可选，如果需要继续某个会话
        }

        try:
            # 向大模型发送POST请求
            response = requests.post(api_url, headers=headers, json=payload)

            # 检查请求是否成功
            if response.status_code == 200:
                response_data = response.json()
                emotion_label = response_data.get("answer", 2)
                # 返回生成的工单摘要
                return JsonResponse({'emotion_label': emotion_label})
            else:
                return JsonResponse({'error': 'Failed to detect emotion', 'details': response.text},
                                    status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# 添加一个新的视图来处理文件上传
class UploadFileView(View):

    def post(self, request, *args, **kwargs):
        # 获取 user_id，确保它是从请求体中获取而不是查询字符串
        user_id = request.POST.get('user', 'abc-123')  # 假设默认用户ID是'abc-123'

        # 获取上传的文件
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        # 构建 API 请求的 URL
        api_url = "https://api.dify.ai/v1/files/upload"
        headers = {
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为你的实际 API 密钥
        }

        # 创建 multipart/form-data 请求体
        files = {
            'file': uploaded_file,
            'user': user_id
        }

        try:
            # 发送 POST 请求
            response = requests.post(api_url, headers=headers, files=files)

            # 检查响应状态
            if response.status_code == 200:
                return JsonResponse({'result': 'success', 'file': response.json()})
            else:
                return JsonResponse({'error': 'Failed to upload file', 'details': response.text},
                                     status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

#获取下一轮建议问题列表
class SuggestedQuestionsView(View):

    def get(self, request, message_id, *args, **kwargs):
        user_id = request.GET.get('user', None)
        if not user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)

        api_url = f"https://api.dify.ai/v1/messages/{message_id}/suggested"
        headers = {
            'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为实际 API 密钥
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(api_url, headers=headers, params={'user': user_id})
            if response.status_code == 200:
                return JsonResponse(response.json())  # 返回建议问题列表
            else:
                return JsonResponse({'error': 'Failed to fetch suggested questions', 'details': response.text},
                                    status=response.status_code)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)


# 新的视图函数用于重置 conversation_id
def new_conversation(request):
    reset_conversation_id()  # 重置当前的会话 ID
    new_conv_id = generate_conversation_id()  # 生成新的会话 ID
    return JsonResponse({'message': '会话已重置', 'conversation_id': new_conv_id})

def get_message_id(request):
    """
    获取 message_id 的接口。
    """
    # 从请求中提取参数
    user_input = request.GET.get('user_input', None)
    conversation_id = request.GET.get('conversation_id', None)

    if not user_input:
        return JsonResponse({'error': 'user_input is required'}, status=400)

    # 定义 API URL
    api_url = "https://api.dify.ai/v1/chat-messages"  # 目标 API 地址

    # API Key
    api_key = "app-EU8DZ6Erz8VvUb55jcH8sfsI"

    # 设置请求头
    headers = {
        'Authorization': f'Bearer {api_key}',  # 替换为你的实际 API 密钥
        'Content-Type': 'application/json'
    }

    # 构建请求体
    request_body = {
        "inputs": {},  # 允许传入 App 定义的各变量值
        "query": user_input,  # 用户提问内容
        "response_mode": "streaming",  # 使用流式模式
        "conversation_id": conversation_id,  # 使用传入的会话ID
        "user": "abc-123",  # 用户标识
    }

    # 发送 POST 请求
    response = requests.post(api_url, headers=headers, json=request_body, stream=True)

    if response.status_code == 200:
        message_id = None  # 存储提取到的 message_id

        # 处理流式返回数据
        for line in response.iter_lines():
            if line:
                event_data = line.decode('utf-8').strip()
                if event_data.startswith("data: "):
                    json_data = event_data[len("data: "):]
                    try:
                        parsed_data = json.loads(json_data)
                        event_type = parsed_data.get("event")

                        if event_type == "message":
                            message_id = parsed_data.get("message_id")  # 提取 message_id
                        elif event_type == "message_end":
                            break  # 流结束

                    except json.JSONDecodeError:
                        print("JSON 解析错误:", json_data)

        if message_id:
            return JsonResponse({'message_id': message_id}, status=200)
        else:
            return JsonResponse({'error': 'message_id not found in response'}, status=404)
    else:
        return JsonResponse({'error': 'Failed to fetch message_id', 'details': response.text}, status=response.status_code)


def get_suggested_questions(request, message_id):
    """
    根据 message_id 获取建议问题列表。
    """
    user_id = request.GET.get('user', 'abc-123')  # 默认用户ID
    api_url = f"https://api.dify.ai/v1/messages/{message_id}/suggested"

    headers = {
        'Authorization': 'Bearer app-EU8DZ6Erz8VvUb55jcH8sfsI',  # 替换为实际 API 密钥
        'Content-Type': 'application/json',
    }
    params = {'user': user_id}

    try:
        # 调用外部 API
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            return JsonResponse(response.json())  # 返回外部 API 的 JSON 响应
        else:
            return JsonResponse({'error': 'Failed to fetch suggested questions', 'details': response.text},
                                status=response.status_code)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

