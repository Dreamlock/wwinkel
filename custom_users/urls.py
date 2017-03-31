from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^login', views.login_view, name='login'),
    url(r'^register_user', views.register_user_view, name='register_user'),
    url(r'^register_organisation', views.register_organisation, name = 'register_organisation')

]
