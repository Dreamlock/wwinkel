from django import forms
from django.forms import ModelForm
from dbwwinkel.models import Question


class DateInput(forms.DateInput):
    input_type = 'date'

class NameForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text','reason', 'purpose', 'deadline']

        labels = {
            'question_text': ('Stel hier je vraag*'),
            'reason': ('Hoe is uw vraag ontstaan?'),
            'purpose': ('Hoe wilt u de resultaten van uw vraag gebruiken?'),
            'deadline': ('Deadline(Laat open indien geen)')
        }

        widgets = {
            'deadline': DateInput()
        }
