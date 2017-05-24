from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UserChangeForm as BaseUserChangeForm
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
    widget = forms.PasswordInput

class LoginForm(forms.Form):
    e_mail = forms.EmailField()
    password = PasswordField()


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
