from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('auth_success', views.authenticated, name="authenticated")
]
