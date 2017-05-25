from django import forms
from dbwwinkel.models import QuestionSubject, Institution, Promotor, Faculty
from django.forms import ModelForm, modelform_factory
from dbwwinkel.models import Question, Student
from django.utils.translation import ugettext_lazy as _
from .models import Education
from dal import autocomplete, forward
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


class InstitutionForm(ModelForm):
    class Meta:
        model = Institution
        fields = ['name']
        labels = {
            'name': _('*Naam instelling')
        }


class PromotorForm(ModelForm):
    class Meta:
        model = Promotor
        fields = ['first_name', 'last_name', 'email', 'tel', 'institution', 'promo_class', 'expertise']

        labels = {
            'first_name': _('*Voornaam'),
            'last_name': _('*Achternaam'),
            'email': _('*E-Mail'),
            'tel': _('Telefoon nummer'),
            'institution': _('*Instelling'),
            'promo_class': _('Bureau'),
            'expertise': _('*Expertise veld')

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

        qs = Institution.objects.exclude(id__in=[inst.id for inst in question.institution.all()])
        self.fields['institution'] = forms.ModelMultipleChoiceField(
            queryset=qs,
            widget=autocomplete.ModelSelect2Multiple(
                url='institution-autocomplete',
                forward=(
                    forward.Const(self.question_id, 'question_id'),
                )
            ),
            label='Voeg toe',
            required=False
        )

        self.fields['institution_delete'].queryset = question.institution

        self.fields['promotor'] = forms.ModelMultipleChoiceField(
            queryset=Promotor.objects.all(),
            required=False,
            label='Voeg toe',
            widget=autocomplete.ModelSelect2Multiple(
                url='promotor-autocomplete',
                forward=(
                    forward.Const(self.question_id, 'question_id'),
                    'institution',
                )
            )
        )
        self.fields['promotor_delete'].queryset = question.promotor

        self.fields['faculty'] = forms.ModelMultipleChoiceField(
            queryset=Faculty.objects.all(),
            widget=autocomplete.ModelSelect2Multiple(
                url='faculty-autocomplete',
                forward=(forward.Const(self.question_id, 'question_id'),
                         'institution',
                         )
            ),
            label='Voeg toe',
            required=False)

        self.fields['faculty_new'] = forms.CharField(max_length=33, required=False, label="Niet in de lijst?")

        self.fields['faculty_delete'] = forms.ModelMultipleChoiceField(
            queryset=question.faculty.all(),
            widget=forms.CheckboxSelectMultiple(),
            label='Verwijderen:',
            required=False
        )

        self.fields['education'] = forms.ModelMultipleChoiceField(
            queryset=Education.objects.all(),
            widget=autocomplete.ModelSelect2Multiple(
                url='education-autocomplete',
                forward=(forward.Const(self.question_id, 'question_id'),
                         'faculty', 'institution',
                         )
            ),
            label='Voeg toe',
            required=False)

        self.fields['education_delete'].queryset = question.education

        self.fields['subject'] = forms.ModelMultipleChoiceField(
            queryset=QuestionSubject.objects.all(),
            widget=autocomplete.ModelSelect2Multiple(
                url='subject-autocomplete',
                forward=(forward.Const(self.question_id, 'question_id'),
                         'education',
                         )
            ),
            label='Voeg toe',
            required=False)

        self.fields['subject_delete'].queryset = question.question_subject

    institution = forms.ModelMultipleChoiceField(queryset=None)
    institution_delete = forms.ModelMultipleChoiceField(
        queryset=Institution.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Verwijderen', required=False
    )

    promotor = forms.ModelMultipleChoiceField(queryset=None)
    promotor_delete = forms.ModelMultipleChoiceField(
        queryset=Promotor.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Verwijderen', required=False
    )

    education_new = forms.CharField(max_length=50, label="Niet in de lijst?", required=False)

    education_delete = forms.ModelMultipleChoiceField(
        queryset=Education.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Verwijderen', required=False
    )

    subject_new = forms.CharField(max_length=50, label="Niet in de lijst?", required=False)

    subject_delete = forms.ModelMultipleChoiceField(
        queryset=QuestionSubject.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Verwijderen', required=False
    )

    education_delete = forms.ModelMultipleChoiceField(
        queryset=Education.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        label='Verwijderen', required=False
    )


class FacetForm(forms.Form):
    own_questions = forms.BooleanField(required=False, label=_('Eigen vragen'))
    status = forms.MultipleChoiceField(required=False, label=_('Status'), choices=Question.STATE_SELECT,
                                       widget=forms.CheckboxSelectMultiple)
    institution = forms.MultipleChoiceField(required=False, label=_('Instelling'), choices=Question.STATE_SELECT,
                                            widget=forms.CheckboxSelectMultiple)

    faculty = forms.MultipleChoiceField(required=False, label=_('Faculteit'), choices=Question.STATE_SELECT,
                                        widget=forms.CheckboxSelectMultiple)

    education = forms.MultipleChoiceField(required=False, label=_('Opleiding'), choices=Question.STATE_SELECT,
                                          widget=forms.CheckboxSelectMultiple)

    subject = forms.MultipleChoiceField(required=False, label=_('Onderwerp'), choices=Question.STATE_SELECT,
                                        widget=forms.CheckboxSelectMultiple)

    promotor = forms.MultipleChoiceField(required=False, label=_('Promotor'), choices=Question.STATE_SELECT,
                                         widget=forms.CheckboxSelectMultiple)

    key_word = forms.MultipleChoiceField(required=False, label=_('Trefwoord'), choices=Question.STATE_SELECT,
                                         widget=forms.CheckboxSelectMultiple)


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'mobile', 'email','education']


class ReserveForm(forms.Form):

    student = forms.ModelChoiceField(queryset = None)


class FacultyForm(forms.ModelForm):

    opleiding = forms.ModelMultipleChoiceField(queryset=Education.objects.all())


    class Meta:
        model = Faculty
        fields = ('__all__')

        labels = {
            'name': 'Naam',
            'institution': 'Instelling',
        }



class EducationForm(forms.ModelForm):


    faculteit =  forms.ModelMultipleChoiceField(queryset=Faculty.objects.all())
    institution = forms.ModelMultipleChoiceField(queryset=Institution.objects.all(), label="Instelling")

    class Meta:
        model = Education
        fields = ('__all__')







def QuestionFormFactory(user, question):
    return modelform_factory(Question, tuple(get_editable_fields(user, question)))


class QuestionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Question
        fields = ()
