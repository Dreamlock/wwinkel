from django.forms import ModelForm
from dbwwinkel.models import Question

class NameForm(ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
