from django import forms
from django.forms import ModelForm, modelform_factory
from dbwwinkel.models import Question, Student
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import datetime
from haystack.forms import FacetedSearchForm
from .models import StudyField
from dal import autocomplete
from dbwwinkel.helpers import get_viewable_states, get_editable_fields
from django.urls import reverse


class DateInput(forms.DateInput):
    input_type = 'date'


class RegisterQuestionForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'public']

        labels = {
            'question_text': _('*Stel hier uw vraag'),
            'reason': _('*Hoe is uw vraag ontstaan?'),
            'purpose': _('*Hoe wilt u de resultaten van uw vraag gebruiken?'),

            'deadline': _('Deadline(Laat open indien geen)'),
            'own_contribution': _('*Kan u een bijdrage leveren aan de kosten?'),
            'remarks': _('Opmerkingen'),
            'public': _('Gaat u er mee akkoord dat de resultaten openbaar zijn en gepubliceerd worden?')
        }

        widgets = {
            'deadline': DateInput()
        }


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['first_name']


class InternalRemarkForm(forms.Form):
    internal_remark = forms.CharField(label=_('Interne opmerking'), widget=forms.Textarea)


class MetaFieldForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question_id = kwargs.pop('question_id')
        super(MetaFieldForm, self).__init__(*args, **kwargs)
        question = Question.objects.get(id=self.question_id)
        self.fields['study_field_delete'].queryset = question.study_field

    study_field = forms.ModelMultipleChoiceField(queryset=StudyField.objects.all(),
                                                 widget=autocomplete.ModelSelect2Multiple(url='study_field-autocomplete', ),
                                                 label='Voeg toe',
                                                 required=False)

    study_field_new = forms.CharField(max_length=50, label="Niet in de lijst?", required=False)

    study_field_delete = forms.ModelMultipleChoiceField(queryset=StudyField.objects.all(),
                                                        widget=forms.CheckboxSelectMultiple(),
                                                        label='Verwijderen', required=False)


def QuestionFormFactory(user, question):
    return modelform_factory(Question, tuple(get_editable_fields(user, question)))

class QuestionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Question
        fields = ()
