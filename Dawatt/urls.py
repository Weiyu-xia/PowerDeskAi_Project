from django.urls import path
from .views import LoginPage
from . import views as Dawatt_views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
    # 大瓦特智能客服界面
    path('DawattChat/', Dawatt_views.DawattView.as_view(), name='DawattChat'),
]