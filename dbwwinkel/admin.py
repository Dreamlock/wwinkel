from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from simple_history import admin as history_admin
from dbwwinkel.models import *
from dbwwinkel.forms import QuestionFormFactory
from custom_users.models import ManagerUser, OrganisationUser


class QuestionStateListFilter(admin.SimpleListFilter):
    title = _('State')
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            return Question.STATE_SELECT

        if request.user.is_manager():
            user = ManagerUser.objects.get(id=request.user.id)
            print(str(user.region.all()))
            if Region.CENTRAL_REGION in user.region.all():
                return (
                    (Question.STATE_SELECT[Question.DRAFT_QUESTION]),
                    (Question.STATE_SELECT[Question.IN_PROGRESS_QUESTION_CENTRAL]),
                    (Question.STATE_SELECT[Question.PROCESSED_QUESTION_CENTRAL]),
                )
            else:
                return (
                    (Question.STATE_SELECT[Question.DRAFT_QUESTION]),
                    (Question.STATE_SELECT[Question.IN_PROGRESS_QUESTION_CENTRAL]),
                    (Question.STATE_SELECT[Question.PROCESSED_QUESTION_CENTRAL]),
                )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        for state in Question.STATE_SELECT:
            #print(self.value(), state[0], str(state[1]))
            if int(self.value()) == state[0]:
                return queryset.filter(state=state[0])


# class QuestionAdmin(admin.ModelAdmin):
class QuestionAdmin(history_admin.SimpleHistoryAdmin):
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

    def has_change_permission(self, request, obj=None):
        # if request.user.has_perm('edit', obj)
        return super().has_add_permission(request)

    def get_fields(self, request, obj=None):
        result = super().get_fields(request, obj)
        print(str(result))
        return result

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj)

    list_filter = (QuestionStateListFilter, 'region')

    filter_horizontal = ('region', 'keyword', 'question_subject')
    readonly_fields = ('creation_date',)

    list_display = ('question_text', 'state',) # 'organisation')
    list_editable = ('state',)
    list_display_links = ('question_text',)



# Register your models here.
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionType)
#admin.site.register(State)
