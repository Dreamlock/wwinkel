from django.shortcuts import render

# Create your views here.

from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from haystack.query import SearchQuerySet

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
            return redirect(detail, question_id = question.id)


    else:
        form = NameForm()

        # if a GET (or any other method) we'll create a blank form
    return render(request, 'dbwwinkel/vraagstelform.html', {'form':form})


def success(request):
    return HttpResponse("Vraag aanvaard")


def list_questions(request):
    val=request.GET.get('search_text','')
    if val == '':
        val = '*'

    print(val)
    sqs = SearchQuerySet().autocomplete(content_auto='ba')

    print(sqs)
    status_lst = State.objects.all()

    context = {'questions': sqs,
               'state_names': status_lst
               }
    return render(request,'dbwwinkel/question_list.html', context)


def detail(request, question_id):
    question = Question.objects.get(id = question_id )
    context = {'question': question}
    return render(request,'dbwwinkel/detail_question.html', context)


@login_required
def edit_question(request, question_id):

    question = Question.objects.get(id = question_id)
    form = NameForm(request.POST or None, instance = question)

    if form.is_valid():
        form.save()
        return redirect(detail, question_id = '1')
    return render(request, 'dbwwinkel/vraagstelform.html',{'form': form })