from django.shortcuts import render

# Create your views here.

from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from haystack.query import SearchQuerySet
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from .forms import NameForm
from .models import Question, State
from custom_users.models import OrganisationUser, ManagerUser, Region


@login_required
@permission_required('dbwwinkel.add_question')
def register_question(request):
    # if this is a POST request we need to process the form data
    # form = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            question = form.save(commit=False)  # We still need to lay out the foreign keys
            org_user = OrganisationUser.objects.get(id = request.user.id)  # Error if creating a question with admin
            question.organisation = org_user.organisation  # Foreign key to the user (organisation in question...)
            question.state = State.objects.get(state=State.DRAFT_QUESTION)
            question.save()
            form.save_m2m()

            # redirect to a new URL:
            return redirect(detail, question_id=question.id)


    else:
        form = NameForm()

        # if a GET (or any other method) we'll create a blank form
    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def list_questions(request):

    # States visible for everyone
    visible_states = [State.STATE_SELECT[State.PUBLIC_QUESTION], State.STATE_SELECT[State.RESERVED_QUESTION]
        , State.STATE_SELECT[State.FINISHED_QUESTION]]

    #search searchbox
    val = request.GET.get('search_text', '')
    if val == '':
        sqs = SearchQuerySet().all().models(Question)

    else:
        sqs = SearchQuerySet().autocomplete(content_auto=val)

    sqs2 = sqs.filter(state__in=[l[0] for l in visible_states])


    if request.user.is_authenticated():

        if request.user.is_organisation():
            user = OrganisationUser.objects.get(id = request.user.id)
            organisation = user.organisation
            organisation_extra = SearchQuerySet().filter(organisation = organisation.id)
            sqs = sqs2 | organisation_extra

        elif request.user.is_manager():

            user = ManagerUser.objects.get(id = request.user.id)

            if user.region.filter(region = Region.CENTRAL_REGION).exists():
                visible_states = State.STATE_SELECT

            else:
                sqs = sqs | SearchQuerySet().filter(region__in = [region.region for region in user.region.all()])
                visible_states.extend([State.STATE_SELECT[State.PROCESSED_QUESTION_CENTRAL],
                                       State.STATE_SELECT[State.IN_PROGRESS_QUESTION_REGIONAL]])
                
    else:
        sqs = sqs2

    if request.POST:
        sqs = sqs.filter(state__in= request.POST.getlist("status"))

        if OrganisationUser.objects.filter(id=request.user.id).exists():
            sqs = sqs | organisation_extra



    context = {'questions': sqs,
               'states': visible_states
               }

    return render(request, 'dbwwinkel/question_list.html', context)


def detail(request, question_id):
    question = Question.objects.get(id=question_id)
    button_template = "dbwwinkel/detail_question/default.html"
    region_list = []

    if request.user.is_authenticated == False: # Then the user is a student
        return student_detail(request, question)

    elif OrganisationUser.objects.filter(id = request.user.id).exists():
        if request.user.has_perm('edit_question', question):
            button_template = "dbwwinnkel/detail_question/organisations.html"

    elif request.user.is_manager():
        user = ManagerUser.objects.get(id=request.user.id)
        if user.region.filter(region=Region.CENTRAL_REGION).exists():
            return central_detail(request, question)

        elif not set(user.region.all()).isdisjoint(question.region.all()):
            return regional_detail(request, question)


    context = {'question': question,
               'button_template': button_template,
               'region_lst': region_list,
               'question_id': question_id}

    return render(request, 'dbwwinkel/detail_question/detail_question_base.html', context)


def student_detail(request, question):
    context = {'question': question}
    return render(request, 'dbwwinkel/detail_question/student.html', context)


def regional_detail(request, question):
    context = {'question': question}
    return render(request, 'dbwwinkel/detail_question/regional_unit.html',context)


def central_detail(request, question):
    region_list = []
    for region in Region.objects.all():
        if region.region != Region.CENTRAL_REGION:
            region_list.append((region, region.region))
    context = {'question': question,
               'region_lst': region_list}
    return render(request, 'dbwwinkel/detail_question/central_unit.html',context)


@login_required
def edit_question(request, question_id):
    question = Question.objects.get(id=question_id)
    # todo: Check if the authentication works.
    try:
        if (request.user.organisation.id == question.organisation.id  # Check user same organisation as question.
                and request.user.has_perm()):
            pass
        else:
            raise PermissionDenied()

    except ValueError:
        raise PermissionDenied()

    form = NameForm(request.POST or None, instance=question)

    if form.is_valid():
        form.save()
        return redirect(detail, question_id='1')
    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def reserve_question(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.user.is_authenticated == False and question.state.state == State.PUBLIC_QUESTION :
        add = ""
        for region in question.region.all():
            add += "{0} ".format(region)
        question.state = State.objects.get(state = State.RESERVED_QUESTION)
        question.save()
        return HttpResponse("Vraag gereserveerd."
                            "\nGelieve contact op te nemen met de medewerker(s) van: {0}".format(add) )



def distribute_question(request, question_id):

    question = Question.objects.get(id = question_id)

    for region in request.POST.getlist('region'):
        region_obj = Region.objects.get(region = region)
        question.region.add(region_obj)

    state = State.objects.get(state= State.PROCESSED_QUESTION_CENTRAL)
    question.state = state
    question.save()

    return HttpResponse("Toegewezen")

def open_question(request, question_id):

    question = Question.objects.get(id = question_id)
    question.state = State.objects.get(state= State.PUBLIC_QUESTION)
    question.save()
    return HttpResponse("Vraag staat publiek")

def assign_question(request, question_id):
    question = Question.objects.get(id = question_id)
    question.state = State.objects.get(state= State.ONGOING_QUESTION)
    question.save()
    return HttpResponse("Vraag is nu lopend")

def round_up_question(request, question_id):
    question = Question.objects.get(id = question_id)
    question.state = State.objects.get(state= State.FINISHED_QUESTION)
    question.save()
    return HttpResponse("Vraag is afgerond")
