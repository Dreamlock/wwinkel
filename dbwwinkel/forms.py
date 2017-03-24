from django import forms
from django.forms import ModelForm
from dbwwinkel.models import Question


class DateInput(forms.DateInput):
    input_type = 'date'

class NameForm(ModelForm):
    class Meta:
        model = Question
        fields = ['question_text','reason', 'purpose','own_contribution','remarks', 'how_know_WW', 'deadline', 'public']

        labels = {
            'question_text': ('*Stel hier uw vraag'),
            'reason': ('*Hoe is uw vraag ontstaan?'),
            'purpose': ('*Hoe wilt u de resultaten van uw vraag gebruiken?'),

            'deadline': ('Deadline(Laat open indien geen)'),
            'own_contribution': ('*Kan u een bijdrage leveren aan de kosten?'),
            'remarks': ('Opmerkingen'),
            'how_know_WW': ('Hoe heeft u de wetenschapswinkel leren kennen?'),
            'public': ('Gaat u er mee akkoord dat de resultaten openbaar zijn en gepubliceerd worden?')
        }

        widgets = {
            'deadline': DateInput()
        }
