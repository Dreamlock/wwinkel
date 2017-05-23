from django import forms

forms.CharField.widget = forms.TextInput(attrs={'class': 'form-control'})
forms.EmailField.widget = forms.EmailInput(attrs = {'class': 'form-control'})
forms.IntegerField.widget = forms.NumberInput(attrs = {'class': 'form-control'})
forms.ModelChoiceField.widget = forms.Select(attrs = {'class': 'form-control'})