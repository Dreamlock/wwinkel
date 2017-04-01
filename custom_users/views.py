from django.shortcuts import render

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

from .forms import LoginForm, OrganisationUserCreationForm, OrganisationForm
from .models import OrganisationUser
@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


def login_view(request):
    # if this is a POST request we need to process the form data

    if request.user.is_authenticated(): # TODO this looks like a decorator?
        return HttpResponse("Already logged in") # TODO redirect to a 404?

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            email = form.cleaned_data['e_mail']
            password = form.cleaned_data['password']

            user = authenticate(email = email, password = password)

            if user is not None:
                login(request, user)
                return HttpResponse('succes') # TODO redirec to to a log in success page?

    else:
        form = LoginForm()

            # redirect to a new URL:
    return render(request, "custom_users/login_form.html", {'form': form})


def register_user_view(request):

    if request.user.is_authenticated(): # TODO this looks like a decorator?
        return HttpResponse("Already logged in") # TODO redirect to a 404?


    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = OrganisationUserCreationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            user = OrganisationUser.objects.get(email=form.cleaned_data['email'])
            if user is not None:
                login(request, user)
                return HttpResponse('succes') # TODO redirec to to a log in success page?"""

    else:
        user_form = OrganisationUserCreationForm()

            # redirect to a new URL:
    return render(request, "custom_users/user_registration_form.html", {'form': user_form})


def register_organisation(request):

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = OrganisationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            return(HttpResponse("Organisatie bewaart"))

    else:
        user_form = OrganisationForm()

            # redirect to a new URL:
    return render(request, "custom_users/organisation_registration_form.html", {'form': user_form})