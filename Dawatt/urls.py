from django.urls import path
from .views import LoginPage
from . import views as Dawatt_views
urlpatterns = [
    # 登录界面
    path('', LoginPage.as_view(), name='login_page'),

    # 大瓦特智能客服界面
    path('DawattChat/', Dawatt_views.DawattView.as_view(), name='DawattChat'),
]