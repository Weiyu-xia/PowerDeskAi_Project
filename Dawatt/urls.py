from django.urls import path
from .views import load_chat_page
from . import views as Dawatt_views
urlpatterns = [
    path('', load_chat_page, name='chat_page'),  # 处理 GET 请求
    path('api/chat/', Dawatt_views.DawattView.as_view(), name='DawattView'),  # 处理 POST 请求
]