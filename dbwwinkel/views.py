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
from custom_users.models import OrganisationUser


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
            question.status = State.objects.get(id=1)
            question.save()
            form.save_m2m()

            # redirect to a new URL:
            return redirect(detail, question_id=question.id)


    else:
        form = NameForm()

        # if a GET (or any other method) we'll create a blank form
    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def list_questions(request):

    organisation_extra = None
    val = request.GET.get('search_text', '')
    if val == '':
        sqs = SearchQuerySet().all().models(Question)

    else:
        sqs = SearchQuerySet().autocomplete(content_auto=val)

    state_names = [_("nieuw"), _("verwerking_centraal"), _("verwerkt_centraal"),_("verwerking_regionaal"),_("vrij"),
                   _("gereserveerd"),_("lopend"),
                   _("afgerond"), _("geweigerd"), _("ingetrokken")]

    using_states = []

    if request.user.is_authenticated() == False: # Unlogged  options for a student
        visible_statuses = [PUBLIC_QUESTION, PUBLIC_QUESTION, FINISHED_QUESTION]
        '''using_states = [
            State.STATE_SELECT[PUBLIC_QUESTION],
            State.STATE_SELECT[PUBLIC_QUESTION],
            State.STATE_SELECT[FINISHED_QUESTION],
        ]'''
        using_states = [State.STATE_SELECT[x] for x in visible_statuses]
        sqs = sqs.filter(status__in = visible_statuses)

    else:
        if request.user.is_organisation()
            using_states = [(5, state_names[4]), (6, state_names[5]), (8, state_names[7])]
            user = OrganisationUser.objects.get(id = request.user.id)
            organisation = user.organisation
            sqs = sqs.filter(status__in =[5, 6, 8])
            organisation_extra = SearchQuerySet().filter(organisation = organisation.id)


    if request.POST:
        sqs = sqs.filter(status__in= request.POST.getlist("status"))

        if OrganisationUser.objects.filter(id=request.user.id).exists():
            sqs = sqs | organisation_extra

    else:
        if OrganisationUser.objects.filter(id=request.user.id).exists():
            sqs = sqs | organisation_extra

    context = {'questions': sqs,
               'states': using_states
               }

    return render(request, 'dbwwinkel/question_list.html', context)


def detail(request, question_id):
    question = Question.objects.get(id=question_id)
    button_template = "dbwwinkel/detail_question_buttons/default.html"

    if request.user.is_authenticated == False: # Then the user is a student
        button_template = "dbwwinkel/detail_question_buttons/student.html"

    elif OrganisationUser.objects.filter(id = request.user.id).exists():
        if request.user.has_perm('edit_question', question):
            button_template = "dbwwinnkel/detail_question_buttons/organisations.html"
    context = {'question': question,
               'button_template': button_template}

    return render(request, 'dbwwinkel/detail_question.html', context)


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
    return HttpResponse("Tijdelijke stub")
    if request.user.is_authenticated == False:
        question =  Question.objects.get(id = question_id )


        if question.status.id == 5:
            pass
