from django.urls import path
from .views import *

app_name = 'worker'
urlpatterns = [
    path('home/<int:worker_id>/', worker_profile_view, name='worker_profile'),
    path('login/', worker_login_view, name='worker_login'),
    path('profil/<int:id>/', worker_home, name='home'),
    path('logout/<int:worker_id>/', worker_logout, name='worker_logout'),
    path('edit/', edit_profile, name='edit_profile'),
    path('messages/<int:id>/', worker_messages_view, name='messages'),
    path('chat/<int:receiver_id>/<int:w_id>/', chat_view, name='chat'),
    path('chat-users/<int:worker_id>', chat_user_list, name='chat_users'),
    path('update-password/<int:worker_id>/', update_password, name='update_pass'),

    # path('messages/<int:id>/', message_detail, name='message_detail'),

]
