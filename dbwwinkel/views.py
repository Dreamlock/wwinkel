from django.shortcuts import render

# Create your views here.

from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .forms import NameForm
from .models import Question,State

@login_required
def register_question(request):
    # if this is a POST request we need to process the form data
    form = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            question = form.save(commit = False) # We still need to lay out the foreign keys
            question.organisation = request.user # Foreign key to the user (organisation in question...)
            question.status = State.objects.get(id = 1)
            question.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('success'))


    else:
        form = NameForm()

        # if a GET (or any other method) we'll create a blank form

    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def success(request):
    return HttpResponse("Vraag aanvaard")


def list_questions(request):

    all_questions = Question.objects.all()
    status_lst = []
    for question in all_questions:
        status = question.status
        status_lst.append(status.state)

    context = {'questions': all_questions,
               'state_names': status_lst
               }
    return render(request,'dbwwinkel/question_list.html', context)



def detail(request, question_id):
    question = Question.objects.get(id = question_id )
    context = {'question': question}
    return render(request,'dbwwinkel/detail_question.html', context)
