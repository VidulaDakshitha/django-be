from django.urls import re_path

from core_apps.task.views.skill_views import SkillView
from core_apps.task.views.subtask_views import SubTaskView

from core_apps.task.views.views import TaskView, TaskGetView

urlpatterns = [
    re_path(r'^task/?(?P<object_id>[\d]+)?/$', TaskView.as_view(), name='user'),
    re_path(r'^retrieve-task/?(?P<object_id>[\d]+)?/$', TaskGetView.as_view(), name='user'),
    re_path(r'^skill/$', SkillView.as_view(), name='user'),
    re_path(r'^subtask/?(?P<object_id>[\d]+)?/$', SubTaskView.as_view(), name='user'),
]
