
from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^register_question', views.register_question, name='register_question'),
    url(r'^success', views.success, name = 'success'),
    url(r'^list_questions', views.list_questions, name = 'list_questions'),
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^search/', include('haystack.urls'))
    ]