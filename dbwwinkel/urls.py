from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register_question', views.register_question, name='register_question'),
]