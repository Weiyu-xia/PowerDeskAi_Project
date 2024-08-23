from django.shortcuts import render
from django.views.generic import TemplateView
from Dawatt.client import Call_Dawatt
from django.views.generic import View
from django.http import JsonResponse
import json
class DawattView(TemplateView):
    template_name = 'Dawatt/welcome.html'

    def post(self, request, *args, **kwargs):
        # 解析 JSON 请求体
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        chat_history = body_data.get('chat_history', [])

        # 生成大模型的回复
        reply = Call_Dawatt(chat_history)

        # 将大模型的回复添加到聊天记录
        chat_history.append({'role': 'assistant', 'content': reply})

        # 将聊天记录转换为格式化字符串
        formatted_history = ""
        for message in chat_history:
            role = '用户' if message['role'] == 'user' else '大瓦特'
            content = message['content']
            formatted_history += f"{role}: {content}；"

        # 输出格式化的聊天记录到控制台
        print('Formatted Chat History:', formatted_history)

        # 返回 JSON 响应，包括生成的回复和格式化的聊天记录
        return JsonResponse({'reply': reply})


# 处理 GET 请求的视图
def load_chat_page(request):
    return render(request, 'Dawatt/welcome.html')