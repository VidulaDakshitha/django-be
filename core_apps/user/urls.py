from django.urls import re_path

from core_apps.user.views.chatroom_views import ChatroomView
from core_apps.user.views.language_views import LanguageView
from core_apps.user.views.user_views import UserView, update_password, LoginView, GetAllUserView, forget_password, \
    RegisterView, GetAllUserSummaryView, GetExternalConsultantsView, GetOrganizationView, connection_accept, \
    ConsultantView, GetUserByRoleView, get_user_status

urlpatterns = [
    re_path(r'^register/$', RegisterView.as_view(), name='user'),
    re_path(r'^user/?(?P<object_id>[\d]+)?/$', UserView.as_view(), name='user'),
    re_path(r'^users/$', GetAllUserView.as_view(), name='user'),
    re_path(r'^users/role/$', GetUserByRoleView.as_view(), name='user'),
    re_path(r'^organization/$', GetOrganizationView.as_view(), name='user'),
    re_path(r'^user-summary/$', GetAllUserSummaryView.as_view(), name='user'),
    re_path(r'^external-consultant/$', GetExternalConsultantsView.as_view(), name='user'),
    re_path(r'^user/?(?P<user_id>[\d]+)?/password/$', update_password, name='user'),
    re_path(r'^forget-password/$', forget_password, name='user'),
    re_path(r'^login/$', LoginView.as_view(), name='user'),
    re_path(r'^language/$', LanguageView.as_view(), name='user'),
    re_path(r'^chatroom/?(?P<object_id>[0-9a-f-]+)?/$', ChatroomView.as_view(), name='chatroom'),
    re_path(r'^connection/$', ConsultantView.as_view(), name='user'),
    re_path(r'^connection-accept/?(?P<conn_id>[\d]+)?/$', connection_accept, name='user'),
    re_path(r'^get-user-status/$', get_user_status, name='get_user_status'),
]
