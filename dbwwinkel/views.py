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
from dal import autocomplete as lightcomplete

from .forms import RegisterQuestionForm, InternalRemarkForm, StudyFieldForm
from .models import Question, StudyField
from custom_users.models import OrganisationUser, ManagerUser, Region

from .search import *



@login_required
@permission_required('dbwwinkel.add_question')
def register_question(request):
    # if this is a POST request we need to process the form data
    # form = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterQuestionForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            question = form.save(commit=False)  # We still need to lay out the foreign keys
            org_user = OrganisationUser.objects.get(id = request.user.id)  # Error if creating a question with admin
            question.organisation = org_user.organisation  # Foreign key to the user (organisation in question...)
            question.state = Question.DRAFT_QUESTION
            question.save()
            form.save_m2m()

            # redirect to a new URL:
            return redirect(detail, question_id=question.id)


    else:
        form = RegisterQuestionForm()

    # if a GET (or any other method) we'll create a blank form
    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def list_questions(request):
    #search searchbox
    if request.POST:
        val = request.POST.get('search_text')

    else:
        val = request.GET.get('search_text', '')

    sqs = autocomplete(SearchQuerySet().all().models(Question),val, Question)

    # States visible for everyone
    visible_states = [Question.STATE_SELECT[Question.PUBLIC_QUESTION], Question.STATE_SELECT[Question.RESERVED_QUESTION]
        , Question.STATE_SELECT[Question.FINISHED_QUESTION]]

    # Fetching all the data specified on user
    if request.user.is_authenticated():

        if request.user.is_organisation():
            user = OrganisationUser.objects.get(id = request.user.id)
            organisation = user.organisation
            organisation_extra = SearchQuerySet().filter(organisation = organisation.id) # the organisations own questions


        elif request.user.is_manager():

            user = ManagerUser.objects.get(id = request.user.id)

            if user.region.filter(region = Region.CENTRAL_REGION).exists():
                visible_states = Question.STATE_SELECT

            else:
                regional_extra = SearchQuerySet().filter(region__in = [region.region for region in user.region.all()])



    if request.POST: #start filtering
        sqs = sqs.filter(state__in= request.POST.getlist("status"))

        if request.POST.getlist("study_field"):
            sqs = sqs.filter(study_field_facet__in=request.POST.getlist("study_field"))

        if OrganisationUser.objects.filter(id=request.user.id).exists():
            if request.POST.getlist('own_question'):
                sqs = sqs | organisation_extra

    else:
        if request.user.is_authenticated():
            if request.user.is_organisation():
                organisation_extra = autocomplete(organisation_extra,val,Question)
                sqs = sqs.filter(state__in=[l[0] for l in visible_states]) | organisation_extra

            elif request.user.is_manager():

                user = ManagerUser.objects.get(id=request.user.id)

                if user.region.filter(region=Region.CENTRAL_REGION).exists(): #No extra filters to apply
                    pass

                else: # + the extra ones bound to this region
                    regional_extra = autocomplete(regional_extra,val,Question)
                    sqs = sqs | regional_extra

        else: # is student
            sqs = sqs.filter(state__in=[l[0] for l in visible_states])


    facets = sqs.facet('study_field_facet')
    study_field = facets.facet_counts()['fields']['study_field_facet']


    own_question = False
    if request.user.is_authenticated() and request.user.is_organisation():
        own_question = True

    true_states = []
    for state in visible_states:
        tuple =(state[0], state[1], True)
        true_states.append(tuple)

    context = {'questions': sqs,
               'states': true_states,
               'study_fields': study_field,
               'search_text': val,
               'own_question': own_question
               }


    return render(request, 'dbwwinkel/question_list.html', context)


def detail(request, question_id):

    question = Question.objects.get(id=question_id)
    organisation = question.organisation

    if request.user.is_authenticated == False: # Then the user is a student
        return student_detail(request, question)

    elif OrganisationUser.objects.filter(id = request.user.id).exists():
        organisation = (OrganisationUser.objects.get(id = request.user.id)).organisation
        if organisation == question.organisation:
            return organisation_detail(request, question, organisation)

    elif request.user.is_manager():
        user = ManagerUser.objects.get(id=request.user.id)
        if user.region.filter(region=Region.CENTRAL_REGION).exists():
            return central_detail(request, question, organisation)

        elif not set(user.region.all()).isdisjoint(question.region.all()):
            return regional_detail(request, question, organisation)


    context = {'question': question,
               'question_id': question_id,
               'organisation': organisation,
               'internal': False}

    return render(request, 'dbwwinkel/detail_question/detail_question_base.html', context)


def student_detail(request, question, organisation):
    context = {'question': question,
               'organisation': organisation,
               'internal': False
               }
    return render(request, 'dbwwinkel/detail_question/student.html', context)


def regional_detail(request, question, organisation):

    context = {'question': question,
               'organisation': organisation,
               'internal': True}

    return render(request, 'dbwwinkel/detail_question/regional_unit.html',context)


def central_detail(request, question, organisation):
    region_list = []
    for region in Region.objects.all():
        if region.region != Region.CENTRAL_REGION:
            region_list.append((region, region.region))
    context = {'question': question,
               'region_lst': region_list,
               'organisation': organisation,
               'internal': True}
    return render(request, 'dbwwinkel/detail_question/central_unit.html',context)

def organisation_detail(request, question, organisation):
    context = {'question': question,
               'organisation': organisation,
               'internal': False}
    return render(request, 'dbwwinkel/detail_question/organisations.html', context)


@login_required
def edit_question(request, question_id):
    question = Question.objects.get(id=question_id)
    # todo: Check if the authentication works.
    '''try:
        if (request.user.organisation.id == question.organisation.id  # Check user same organisation as question.
                and request.user.has_perm()):
            pass
        else:
            raise PermissionDenied()

    except ValueError:
        raise PermissionDenied() '''

    form = RegisterQuestionForm(request.POST or None, instance=question)

    if form.is_valid():
        form.save()
        return redirect(detail, question_id= question_id)
    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def reserve_question(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.user.is_authenticated == False and question.state.state == Question.PUBLIC_QUESTION :
        add = ""
        for region in question.region.all():
            add += "{0} ".format(region)
        question.state = Question.RESERVED_QUESTION
        question.save()
        return HttpResponse("Vraag gereserveerd."
                            "\nGelieve contact op te nemen met de medewerker(s) van: {0}".format(add) )



def distribute_question(request, question_id):

    question = Question.objects.get(id = question_id)

    for region in request.POST.getlist('region'):
        region_obj = Region.objects.get(region = region)
        question.region.add(region_obj)

    question.state = Question.IN_PROGRESS_QUESTION_REGIONAL
    question.save()

    return HttpResponse("Toegewezen")

def open_question(request, question_id):

    question = Question.objects.get(id = question_id)
    question.state = Question.PUBLIC_QUESTION
    question.save()
    return HttpResponse("Vraag staat publiek")

def assign_question(request, question_id):
    question = Question.objects.get(id = question_id)
    question.state = Question.ONGOING_QUESTION
    question.save()
    return HttpResponse("Vraag is nu lopend")

def round_up_question(request, question_id):
    question = Question.objects.get(id = question_id)
    question.state = Question.FINISHED_QUESTION
    question.save()
    return HttpResponse("Vraag is afgerond")

def deny_question(request, question_id):
    """FAKE NEWS"""

    question = Question.objects.get(id = question_id)
    question.state = Question.DENIED_QUESTION
    question.save()
    return HttpResponse("Vraag is geweigerd")


def revoke_question(request, question_id):

    question = Question.objects.get(id = question_id)
    question.state = Question.REVOKED_QUESTION
    question.save()
    return HttpResponse("Vraag is terug getrokken")



def distribute_intake(request, question_id):
    question = Question.objects.get(id=question_id)

    region = Region.objects.get(region = request.POST.getlist('region')[0])
    question.region.add(region)
    question.state = Question.IN_PROGRESS_QUESTION_REGIONAL
    question.save()

    return redirect('detail_question',question_id =int(question_id))


def internal_remark(request, question_id):
    question = Question.objects.get(id = question_id)

    if request.method == 'POST':
        form = InternalRemarkForm(request.POST)
        if form.is_valid():
            new_remark = form.cleaned_data['internal_remark']
            question.internal_remarks = new_remark
            question.save()
            return redirect('detail_question', question_id = question_id)

    else:
        existing_remark = question.internal_remarks
        data = {'internal_remark': existing_remark}
        form = InternalRemarkForm(initial = data)


    return render(request, 'dbwwinkel/internal_remark.html', {'form': form, 'question_id':question_id})


class StudyFieldAutocomplete(lightcomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = StudyField.objects.all()

        if self.q:
            qs = qs.filter(study_field__istartswith=self.q)

        return qs


def edit_study_field(request, question_id):

    form = StudyFieldForm()
    return render(request, 'dbwwinkel/edit_study_field.html', {'form': form})

