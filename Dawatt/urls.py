from django.urls import path
from . import views as Dawatt_views
from django.contrib.auth import views as auth_views
from .views import LoginPage, LogoutView, emotion_analysis, new_conversation, MessageHistoryView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),

    # 大瓦特智能客服界面
    path('DawattChat/', Dawatt_views.DawattView.as_view(), name='DawattChat'),
    # 添加情绪识别的路由
    path('DawattChat/emotion/', emotion_analysis, name='emotion_analysis'),

    path('DawattChat/new-conversation/', new_conversation, name='new_conversation'),

    path('messages/', MessageHistoryView.as_view(), name='message_history'),

]