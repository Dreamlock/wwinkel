
from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^register_question', views.register_question, name='register_question'),
    url(r'^success', views.success, name = 'success'),
    url(r'^list_questions', views.list_questions, name = 'list_questions'),
    url(r'^detail_organisation/(?P<question_id>[0-9]+)', views.detail, name='detail_organisation'),
    url(r'^edit_question/(?P<question_id>[0-9]+)',views.edit_question, name = 'edit_question'),
    url(r'^search/', include('haystack.urls'))
    ]