from django import forms

forms.CharField.widget = forms.TextInput(attrs={'class': 'form-control'})
forms.EmailField.widget = forms.EmailInput(attrs = {'class': 'form-control'})