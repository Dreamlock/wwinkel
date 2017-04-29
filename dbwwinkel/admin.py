from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from .models import *
from custom_users.models import ManagerUser, OrganisationUser


class QuestionStateListFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return State.STATE_SELECT

        if request.user.is_manager():
            user = ManagerUser.objects.get(id=request.user.id)
            print(str(user.region.all()))
            if Region.CENTRAL_REGION in user.region.all():
                return (
                    (State.STATE_SELECT[State.DRAFT_QUESTION]),
                    (State.STATE_SELECT[State.IN_PROGRESS_QUESTION_CENTRAL]),
                    (State.STATE_SELECT[State.PROCESSED_QUESTION_CENTRAL]),
                )
            else:
                return (
                    (State.STATE_SELECT[State.DRAFT_QUESTION]),
                    (State.STATE_SELECT[State.IN_PROGRESS_QUESTION_CENTRAL]),
                    (State.STATE_SELECT[State.PROCESSED_QUESTION_CENTRAL]),
                )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        for state in State.STATE_SELECT:
            print(self.value(), state[0], str(state[1]))
            if int(self.value()) == state[0]:
                return queryset.filter(state__state=state[0])


class QuestionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.is_manager():
            user = ManagerUser.objects.get(id=request.user.id)
            return qs.filter(region__in=user.region.all())

        if request.user.is_organisation():
            user = OrganisationUser.objects.get(id=request.user.id)
            return qs.filter(organisation=user.organisation)

    def has_add_permission(self, request):
        return super().has_add_permission(request)

    list_filter = (QuestionStateListFilter, 'region')

    filter_horizontal = ('region', 'keyword', 'question_subject', 'study_field')
    readonly_fields = ('creation_date',)

    list_display = ('question_text', 'state', 'organisation')
    list_editable = ('state',)
    list_display_links = ('organisation',)

# Register your models here.
admin.site.register(Question, QuestionAdmin)
#admin.site.register(State)
