
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createPost", views.createPost, name="createPost"),
    path("following", views.following, name="following"),
    path("userProfile/<int:pk>/", views.userProfile, name="userProfile"),
    path("followProfile/<int:pk>/", views.followProfile, name="followProfile"),
    path('like/', views.like),
    path('edit_post/', views.edit_post),
]
