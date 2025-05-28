from django.urls import path

from manager.views import *

app_name = 'manager'
urlpatterns = [
    path('manager-register/', manager_register, name='m_register'),
    path('manager-login/', manager_login, name='m_login'),
    path('profil/', manager_profile, name='profil'),
    path('logout/', logout_view, name='logout'),
    path('add-worker/<int:id>/', add_worker, name='add_worker'),
    path('worker-list/', worker_list, name='worker_list'),
    path('', home, name='home'),
    path('add-daily-work/', add_daily_work, name='add_daily_work'),
    path('worker-detail/<int:worker_id>/', worker_detail, name='worker_detail'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('create-message/', create_message_view, name='create_message'),
    path('chat-users/', manager_chat_l, name='m_chat_u'),
    path('manager-chat/<int:id>', manager_chat_detail, name='m_chat'),
    path('daily_reports/', daily_reports, name='daily_reports'),
    path('message-edit/<int:message_id>/', edit_message, name='edit_message'),
    path('mark_as_read/<int:message_id>/', mark_as_read, name='mark_as_read'),
    path('message-delete/<int:message_id>/', delete_message, name='delete_message'),

]
