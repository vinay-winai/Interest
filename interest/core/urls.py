from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("connect/", views.connect, name="connect"),
    path("get_other_user_details/", views.get_other_user_details, name="get_other_user_details"),
]