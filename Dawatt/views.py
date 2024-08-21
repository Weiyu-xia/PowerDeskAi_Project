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
        user_input = body_data.get('user_input', '')

        reply = Call_Dawatt(user_input)
        return JsonResponse({'reply': reply})


# 处理 GET 请求的视图
def load_chat_page(request):
    return render(request, 'Dawatt/welcome.html')