from django.shortcuts import render

# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView
from .forms import *
from .models import OrganisationUser
@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


def login_view(request):
    # if this is a POST request we need to process the form data

    if request.user.is_authenticated(): # TODO this looks like a decorator?   ## extra comment: If used as a decorator, denies permission to this view when not logged in.
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
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return HttpResponseRedirect('/dbwwinkel/list_questions?search_text=') # TODO redirect to to a log in success page?



    else:
        form = LoginForm()

            # redirect to a new URL:
    return render(request, "custom_users/login_form.html", {'form': form})

def register_organisation(request):


    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        organisation_form = OrganisationForm(request.POST, prefix="organisation")
        address_form = AdressForm(request.POST, prefix='address')
        user_form = BaseOrganisationUserForm(request.POST, prefix='user')


        # check whether it's valid:
        if organisation_form.is_valid() and address_form.is_valid() and user_form.is_valid():

            organisation = organisation_form.save(commit = False)
            address=address_form.save()
            user = user_form.save(commit = False)

            organisation.address= address
            organisation.save()

            user.organisation = organisation

            # todo: add permissions.
            user.save()

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return(HttpResponseRedirect('/dbwwinkel/list_questions?search_text='))
    else:
        organisation_form = OrganisationForm(prefix="organisation")
        address_form = AdressForm( prefix='address')
        user_form =BaseOrganisationUserForm(prefix='user')

        organisation_form.fields['legal_entity'].queryset = LegalEntity.objects.all()
        organisation_form.fields['type'].queryset = OrganisationType.objects.all()
        # redirect to a new URL:

    context = {
        'organisation_form': organisation_form,
        'address_form': address_form,
        'user_form': user_form
    }
    return render(request, "custom_users/organisation_registration_form.html",context)


@login_required
def organisation_detail(request):
    usr = OrganisationUser.objects.get(email=request.user.email)
    organisation = usr.organisation
    context = {'organisation': organisation}
    return render(request, 'custom_users/organisation_detail.html', context)

@login_required
def edit_organisation(request, organisation_id):
    organisation = Organisation.objects.get(id=organisation_id)
    form = OrganisationForm(request.POST or None, instance=organisation)

    if form.is_valid():
        form.save()
        return redirect(organisation_detail)
    return render(request, 'custom_users/organisation_registration_form.html', {'form': form})