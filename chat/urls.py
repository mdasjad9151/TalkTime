from django.urls import path
from . import views

urlpatterns = [
  path('chat/<str:username>/', views.chat_view, name='chat'),

  path('home/', views.home, name='home'),
  path('fetch_messages/<str:username>/', views.fetch_messages, name='fetch_messages'),
  path('add_friends/', views.add_friends, name='add_friends'),
    path('add_friend/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('requests/', views.show_requests, name='show_requests'),
     path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
]
