from . import views
from django.conf.urls import url, include
from .autocomplete import *

urlpatterns = [
    # Register urls
    url(r'^register_question', views.register_question, name='register_question'),
    url(r'register_institution/(?P<question_id>[0-9]+)', views.register_institution, name='register_institution'),
    url(r'register_promotor/(?P<question_id>[0-9]+)', views.register_promotor, name='register_promotor'),
    # Rest

    url(r'^organisation_detail/(?P<pk>[0-9]+)', views.OrganisationDetail.as_view(), name='organisation_detail'),
    url(r'^institution_detail/(?P<pk>[0-9]+)', views.InstitutionDetail.as_view(), name='institution_detail'),
    url(r'^faculty_detail/(?P<pk>[0-9]+)', views.FacultyDetail.as_view(), name='faculty_detail'),
    url(r'^education_detail/(?P<pk>[0-9]+)', views.EducationDetail.as_view(), name='education_detail'),
    url(r'^contact_detail/(?P<pk>[0-9]+)', views.ContactDetail.as_view(), name='contact_detail'),
    url(r'^promotor_detail/(?P<pk>[0-9]+)', views.PromotorDetail.as_view(), name='promotor_detail'),

    url(r'^list_questions', views.list_questions, name='list_questions'),
    url(r'^list_questions/(?P<admin_filter>[a-z]+)', views.list_questions, name='list_questions_filter'),

    url(r'^detail_question/(?P<question_id>[0-9]+)', views.detail, name='detail_question'),

    url(r'distribute_intake/(?P<question_id>[0-9]+)', views.distribute_intake, name='distribute_intake'),
    url(r'finish_intake/(?P<question_id>[0-9]+)', views.finish_intake, name='finish_intake'),
    url(r'^distribute_question/(?P<question_id>[0-9]+)', views.distribute_to_public, name='distribute_question_public'),
    url(r'^open_question/(?P<question_id>[0-9]+)', views.open_question, name='open_question'),
    url(r'^reserve_question/(?P<question_id>[0-9]+)', views.reserve_question, name='reserve_question'),
    url(r'^interested_in_question/(?P<question_id>[0-9]+)', views.interested_in_question_view, name='interested_in_question'),
    url(r'^assign_question/(?P<question_id>[0-9]+)', views.assign_question, name='assign_question'),
    url(r'round_up_question/(?P<question_id>[0-9]+)', views.round_up_question, name='round_up_question'),
    url(r'deny_question/(?P<question_id>[0-9]+)', views.deny_question, name='deny_question'),
    url(r'revoke_question/(?P<question_id>[0-9]+)', views.revoke_question, name='revoke_question'),

    url(r'^edit_question/(?P<question_id>[0-9]+)', views.edit_question, name='edit_question'),
    url(r'internal_remark/(?P<question_id>[0-9]+)', views.internal_remark, name='internal_remark'),
    url(r'edit_meta_info/(?P<question_id>[0-9]+)', views.edit_meta_info, name='edit_meta_info'),

    url(r'admin_to_process/', views.administration_view_to_process, name='admin_to_process'),
    url(r'admin_new/', views.administration_view_new, name='admin_new'),
    url(r'admin_intake_process/', views.administration_view_intake_in_progress, name='admin_intake_process'),
    url(r'admin_afer_intake/', views.administration_view_intake_done, name='admin_intake_done'),
    url(r'admin_in_progress_regional/', views.administration_view_in_regional_process, name='admin_regional_process'),
    url(r'admin_public/', views.administration_view_public, name='admin_public'),
    url(r'admin_reserved/', views.administration_view_reserved, name='admin_reserved'),
    url(r'admin_ongoing/', views.administration_view_on_going, name='admin_ongoing'),
    url(r'admin_finished/', views.administration_view_finished, name='admin_finished'),
    url(r'admin_denied/', views.administration_view_denied, name='admin_denied'),
    url(r'admin_revoked/', views.administration_view_revoked, name='admin_revoked'),
    url(r'admin_regional_progress_all/', views.administration_view_in_regional_process_all,
        name='admin_regional_process_all'),

    url(r'admin_my_question/', views.administration_view_my_questions, name='admin_my_question'),

    url(r'admin_organisations/', views.admin_organisation_table_view, name='admin_organisations'),
    url(r'admin_contacts/', views.admin_organisation_contact_view, name='admin_contacts'),

    url(r'admin_institution/', views.admin_institution_view, name='admin_institutions'),
    url(r'admin_faculty/', views.admin_faculty_view, name='admin_faculty'),
    url(r'admin_education/', views.admin_education_view, name='admin_education'),
    url(r'admin_promotors/', views.admin_promotor_view, name='admin_promotor'),

    url(r'^institution-autocomplete/$',
        InstitutionAutocomplete.as_view(),
        name='institution-autocomplete'),

    url(r'^promotor-autocomplete/$',
        PromotorAutocomplete.as_view(),
        name='promotor-autocomplete'),

    url(r'^faculty-autocomplete/$',
        FacultyAutocomplete.as_view(),
        name='faculty-autocomplete'),

    url(r'^education-autocomplete/$',
        EducationAutocomplete.as_view(create_field='education'),
        name='education-autocomplete'),

    url(r'^subject-autocomplete/$',
        SubjectAutocomplete.as_view(create_field='subject'),
        name='subject-autocomplete'),

    url(r'^search/', include('haystack.urls')),

]
