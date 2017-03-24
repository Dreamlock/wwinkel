from django.shortcuts import render

# Create your views here.

from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .forms import NameForm
from .models import Intake

def register_question(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.save(commit = False) # We still need to lay out the foreign keys
            # intake = Intake.objects.create()

            # Adding extra metadata that comes with a question
            # Starting with creating intake



            # redirect to a new URL:
            return HttpResponseRedirect(reverse('success'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def success(request):
    return HttpResponse("Vraag aanvaard")
