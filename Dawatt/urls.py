from django.urls import path
from . import views as Dawatt_views
from django.contrib.auth import views as auth_views
from .views import LoginPage, LogoutView, emotion_analysis, new_conversation, MessageHistoryView, ConversationsListView, \
    DeleteConversationView, RenameConversationView, GenerateTicketView

urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),

    # 大瓦特智能客服界面
    path('DawattChat/', Dawatt_views.DawattView.as_view(), name='DawattChat'),

    # 添加情绪识别的路由
    path('DawattChat/emotion/', emotion_analysis, name='emotion_analysis'),

    path('DawattChat/new-conversation/', new_conversation, name='new_conversation'),

    path('messages/', MessageHistoryView.as_view(), name='message_history'),

    path('conversations', ConversationsListView.as_view(), name='conversation_list'),

    path('delete_conversation/<str:conversation_id>/', DeleteConversationView.as_view(), name='delete_conversation'),

    path('rename_conversation/<str:conversation_id>/', RenameConversationView.as_view(), name='rename_conversation'),

    path('generate_ticket/', GenerateTicketView.as_view(), name='generate_ticket'),

]