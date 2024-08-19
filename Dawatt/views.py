from django.shortcuts import render
from django.views.generic import TemplateView

from Dawatt.client import Call_Dawatt


class DawattView(TemplateView):
    template_name = 'Dawatt/welcome.html'

    extra_context = {
        'reply': Call_Dawatt("介绍一下南方电网"),

    }
