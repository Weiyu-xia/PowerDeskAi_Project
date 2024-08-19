from django.urls import path
from . import views as Dawatt_views

urlpatterns = [
    path('', Dawatt_views.DawattView.as_view(), name='DawattView'),
]