from . import views
from django.contrib.auth.views import password_change, password_change_done
from django.conf.urls import url, include

# app_name = 'custom_users'
urlpatterns = [
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^login', views.login_view, name='login'),
    url(r'password_change/$', password_change, {
        'template_name': 'custom_users/password_change_form.html',
        'post_change_redirect': 'password_change_done'},
        name='password_change'),
    url(r'password_change_done/$', password_change_done, {
        'template_name': 'custom_users/password_change_done.html'},
        name='password_change_done'),
    url(r'^register_organisation', views.register_organisation, name='register_organisation'),
    url(r'^organisation_detail', views.organisation_detail, name='organisation_detail'),
    url(r'^edit_organisation/(?P<organisation_id>[0-9]+)', views.edit_organisation, name='edit_organisation')
]
