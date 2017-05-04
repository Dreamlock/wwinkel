from django import forms
from django.forms import ModelForm
from dbwwinkel.models import Question, Student
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import datetime
from haystack.forms import FacetedSearchForm

class DateInput(forms.DateInput):
    input_type = 'date'



class NameForm(ModelForm):

    class Meta:
        model = Question
        fields = ['question_text','reason', 'purpose','own_contribution','remarks', 'how_know_WW', 'deadline', 'public', 'study_field']

        labels = {
            'question_text': _('*Stel hier uw vraag'),
            'reason': _('*Hoe is uw vraag ontstaan?'),
            'purpose': _('*Hoe wilt u de resultaten van uw vraag gebruiken?'),

            'deadline': _('Deadline(Laat open indien geen)'),
            'own_contribution': _('*Kan u een bijdrage leveren aan de kosten?'),
            'remarks': _('Opmerkingen'),
            'how_know_WW': _('Hoe heeft u de wetenschapswinkel leren kennen?'),
            'public': _('Gaat u er mee akkoord dat de resultaten openbaar zijn en gepubliceerd worden?')
        }

        widgets = {
            'deadline': DateInput()
        }

class StudentForm(ModelForm):

    class Meta:
        model = Student
        fields = ['first_name']


