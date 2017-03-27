from django.shortcuts import render

# Create your views here.

from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import NameForm

@login_required
def register_question(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            question = form.save(commit = False) # We still need to lay out the foreign keys
            question.organisation = request.user # Foreign key to the user (organisation in question...)
            question.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('success'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def success(request):
    return HttpResponse("Vraag aanvaard")
