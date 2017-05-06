from . import views
from django.conf.urls import url, include

urlpatterns = [
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^login', views.login_view, name='login'),
    url(r'^register_organisation', views.register_organisation, name = 'register_organisation'),
    url(r'^organisation_detail', views.organisation_detail, name='organisation_detail'),
    url(r'^edit_organisation/(?P<organisation_id>[0-9]+)', views.edit_organisation, name='edit_organisation')
]
