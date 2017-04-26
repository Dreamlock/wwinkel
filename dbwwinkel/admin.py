from django.contrib import admin

from .models import *


class QuestionAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_date',)
    list_display = ('question_text', 'state', 'organisation')
    filter_horizontal = ('region', 'keyword', 'question_subject', 'study_field')

# Register your models here.
admin.site.register(Question, QuestionAdmin)
#admin.site.register(State)
