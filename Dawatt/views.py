from django.shortcuts import render
from django.views.generic import TemplateView
from Dawatt.client import Call_Dawatt


class DawattView(TemplateView):
    template_name = 'Dawatt/welcome.html'

    # 从表单获取用户的输入
    def post(self, request, *args, **kwargs):
        user_input = request.POST.get('user_input', '')
        reply = Call_Dawatt(user_input)
        context = self.get_context_data(reply=reply, user_input=user_input)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
