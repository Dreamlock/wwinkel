from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'custom_users/login.html'}, name = 'login'),

]
