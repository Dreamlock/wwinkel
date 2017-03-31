from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UserChangeForm as BaseUserChangeForm
from .models import User, OrganisationUser, Organisation
from django import forms


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
        # fields = ('email', 'telephone', )


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

    class Meta:
        model = Organisation
        fields = '__all__'
