from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UserChangeForm as BaseUserChangeForm
from django.forms.utils import ErrorList
from haystack.forms import FacetedSearchForm

from .models import User, OrganisationUser, Organisation, Address, OrganisationType, LegalEntity
from django import forms
from django.utils.translation import ugettext_lazy as _


class UserCreationForm(BaseUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('email', 'telephone', 'gsm')



class UserChangeForm(BaseUserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = '__all__'


class OrganisationUserCreationForm(BaseUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganisationUser
        fields = ['organisation','email','first_name','last_name','telephone']



class OrganisationUserChangeForm(BaseUserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganisationUser
        fields = '__all__'


class ManagerUserCreationForm(BaseUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganisationUser
        fields = '__all__'
        # fields = ('email', 'telephone', )


class ManagerUserChangeForm(BaseUserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganisationUser
        fields = '__all__'

class PasswordField(forms.CharField):
    widget = forms.PasswordInput(attrs = {'class': 'form-control'})

class LoginForm(forms.Form):

    e_mail = forms.EmailField()
    password = PasswordField()

    def clean(self):
        if not User.objects.filter(email = self.cleaned_data['e_mail']).exists():
            self.errors['e_mail'] = ErrorList(['Ongeldig Mail adres'])

        user = authenticate(email=self.cleaned_data['e_mail'], password=self.cleaned_data['password'])

        if user is None:
            self.errors['password'] = ErrorList(['Ongeldig wachtwoord'])


class OrganisationForm(forms.ModelForm):

    def __init__(self,*args, **kwargs):
        super(OrganisationForm,self).__init__(*args, **kwargs)

    class Meta:
        model = Organisation
        fields = ['name', 'recognised_abbreviation', 'legal_entity', 'type', 'telephone','fax',
                  'mail','website', 'goal', 'remarks', 'know_from']

        labels = {
            'name': 'Naam Organisatie',
            'recognised_abbreviation': 'Afkorting Organisatie',
            'legal_entity': 'Juridische entiteit',
            'telephone': 'Telefoon',
            'website': 'website',
            'goal': 'Doel organisatie',
            'remarks': 'Opmerkingen',
            'type': 'Soort',
            'know_from': 'Van waar ken je ons'

        }
        help_texts = {
            'telephone': _('Nummer waarop we het bedrijf kunnen contacteren')
        }


class AdressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ['street_name', 'street_number','city', 'postal_code','province']

        labels = {
            'province': 'Provincie',
            'city': 'Stad',
            'postal_code': 'Postcode',
            'street_name': 'Straat naam',
            'street_number': 'Postnummer'
        }

class BaseOrganisationUserForm(OrganisationUserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganisationUser
        fields = ['email', 'first_name', 'last_name', 'telephone']
        labels = {'telephone': 'Telefoon'}


class FacetedProductSearchForm(FacetedSearchForm):

    def __init__(self, *args, **kwargs):
        data = dict(kwargs.get("data", []))
        self.institutionns = data.get('institution', [])
        self.brands = data.get('brand', [])
        super(FacetedProductSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        sqs = super(FacetedProductSearchForm, self).search()
        if self.institutionns:
            query = None
            for institution in self.institutionns:
                if query:
                    query += u' OR '
                else:
                    query = u''
                query += u'"%s"' % sqs.query.clean(institution)
            sqs = sqs.narrow(u'institution_exact:%s' % query)

        return sqs
