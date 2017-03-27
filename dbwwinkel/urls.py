from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register_question', views.register_question, name='register_question'),
    url(r'^success', views.success, name = 'success'),
    url(r'^list_questions', views.list_questions, name = 'list_questions')
]