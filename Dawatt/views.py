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

        # 返回 JSON 响应
        return JsonResponse({'reply': reply})


# 处理 GET 请求的视图
def load_chat_page(request):
    return render(request, 'Dawatt/welcome.html')