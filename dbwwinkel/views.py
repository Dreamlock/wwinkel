from django.shortcuts import render

# Create your views here.

import time
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from haystack.query import SearchQuerySet

from custom_users.forms import AdressForm
from .forms import *
from .models import Question, Education, QuestionSubject, FacultyOf, QuestionGroups
from custom_users.models import OrganisationUser, ManagerUser, Region, Organisation
from operator import itemgetter
from .search import autocomplete as search, query_extra_content, query_on_states
import os

from django.views.generic import View, ListView, DetailView
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView

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
            org_user = OrganisationUser.objects.get(id=request.user.id)  # Error if creating a question with admin
            question.organisation = org_user.organisation  # Foreign key to the user (organisation in question...)
            question.state = Question.NEW_QUESTION
            new_group = QuestionGroups.objects.create()
            new_group.save()
            question.question_group = new_group
            question.save()
            form.save_m2m()

            # redirect to a new URL:
            return redirect(detail, question_id=question.id)

    else:
        form = RegisterQuestionForm()

    # if a GET (or any other method) we'll create a blank form
    return render(request, 'dbwwinkel/templates/forms_creation/vraagstelform.html', {'form': form})



def list_questions(request, admin_filter=None):
    val = request.GET.get('search_text', '')
    sqs = search(SearchQuerySet(), val, Question)


    facet_form = FacetForm(request.GET)
    status_lst = Question.STATE_SELECT
    # we filter all questions that are not public, reserved, or finished, we don't do this for the central maanger
    if not (request.user.is_authenticated() and request.user.is_manager() and request.user.is_central_manager()):
        status_lst = [
            status_lst[Question.PUBLIC_QUESTION],
            status_lst[Question.RESERVED_QUESTION],
            status_lst[Question.FINISHED_QUESTION]
        ]
        sqs = sqs.filter(state__in=[status[0] for status in status_lst])

    facet_form.fields['status'].choices = status_lst

    sqs = sqs.facet('state_facet')
    choice_facet = (sqs.facet_counts()['fields']['state_facet'])
    choice_facet2 = []
    for choice in choice_facet:
        choice_facet2.append((int(choice[0]), int(choice[1])))
    choice_facet = choice_facet2
    choice_facet = sorted(choice_facet, key=itemgetter(0))

    for i in range(len(choice_facet)):
        if i != choice_facet[i][0]:
            choice_facet.insert(i, (i, 0))

    if not request.user.is_authenticated:
        choice_facet = [choice_facet[4], choice_facet[5], choice_facet[7]]
    if request.user.is_authenticated and not request.user.is_superuser:
        if not request.user.is_central_manager():
            choice_facet = [choice_facet[4], choice_facet[5], choice_facet[7]]
    facet_count = [choice_facet, choice_facet]

    # Filter out the status of questions needed
    if facet_form.data.get('status', False):
        data = facet_form.data['status']
        facet_form.fields['status'].initial = list(map(int, data))
        sqs = query_on_states(sqs, data)

    # Check if some extra questions need to be added to the queryset
    if facet_form.data.get('own_questions', False):
        sqs = query_extra_content(request.user, sqs)

    # Filter based on Facets
    field_lst = ['institution', 'faculty', 'education', 'subject', 'promotor', 'key_word']
    # Calculate the facets
    for field in field_lst:

        sqs = sqs.facet('{0}_facet'.format(field), mincount=1, limit=5)
        choice_facet = (sqs.facet_counts()['fields']['{0}_facet'.format(field)])
        choice_facet = sorted(choice_facet, reverse=True, key=itemgetter(1))
        helper_lst = []
        for choice in choice_facet:
            name = choice[0]
            if len(name) > 25:
                counter = 0
                for c in (name):
                    counter += 1
                    if c == ' ':
                        if counter > 25:
                            name = name[:counter] + '...'
                            break
            helper_lst.append((choice[0], name))
        facet_form.fields[field].choices = helper_lst
        facet_count.append(choice_facet)

        try:
            facet_data = facet_form.data.getlist(field, False)
            if facet_data:
                sqs = sqs.filter(**{'{0}_facet__in'.format(field): facet_data})
                facet_form.fields[field].initial = list(map(str, facet_data))
        except:
            pass

    user_type = 'student'
    if request.user.is_authenticated:
        if request.user.is_organisation():
            user_type = 'organisation'
        elif request.user.is_manager() or request.user.is_superuser:
            user_type = 'manager'

    if request.user.is_authenticated:
        if admin_filter is None:
            pass
        elif admin_filter == 'nieuw':
            if request.user.is_organisation():
                pass
            elif request.user.is_manager():
                if request.user.is_central_manager():
                    sqs.filter(status__in=(Question.NEW_QUESTION, Question.IN_PROGRESS_QUESTION_CENTRAL))
                if request.user.is_regional_manager():
                    sqs.filter(status_in=(Question.INTAKE_QUESTION, Question.IN_PROGRESS_QUESTION_REGIONAL))
        elif admin_filter == 'alle_vragen':
            pass

    context = {
        'questions': sqs[:200],
        'facet_form': facet_form,
        'search_text': val,
        'facet_count': facet_count,
        'user_type': user_type,
    }
    return render(request, 'dbwwinkel/facet_results/question_list.html', context)


def detail(request, question_id):
    question = Question.objects.get(id=question_id)
    organisation = question.organisation
    template_lst = []

    context = {'question': question,
               'question_id': question_id,
               'organisation': organisation,
               'internal': False,
               'options': template_lst,
               'region_lst': Region.objects.exclude(region=Region.CENTRAL_REGION)}

    return render(request, 'dbwwinkel/question_detail/detail_question.html', context)


@login_required
def edit_question(request, question_id):
    question = Question.objects.get(id=question_id)
    form = RegisterQuestionForm(request.POST or None, instance=question)

    if form.is_valid():
        form.save()
        return redirect(detail, question_id=question_id)
    return render(request, 'dbwwinkel/templates/forms_creation/vraagstelform.html', {'form': form})


def reserve_question(request, question_id):
    # if this is a POST request we need to process the form data
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ReserveForm(request.POST)
        form.fields['student'].queryset = question.potential_students.all()
        # check whether it's valid:

        if form.is_valid():
            student = form.cleaned_data['student']

            question.student = student
            question.potential_students.remove(student)
            question.state = Question.RESERVED_QUESTION
            question.save()

            return redirect(detail, question_id=question_id)

    else:
        form = ReserveForm()
        form.fields['student'].queryset = question.potential_students.all()

    print(question.potential_students.all())

    return render(request, 'dbwwinkel/templates/confirmations/reserve_question.html',
                  {'form': form, 'question': question})


def assign_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.ONGOING_QUESTION

    for student in question.potential_students.all():
        student.delete()
        student.save()
    question.potential_students.all().delete()
    question.save()
    return redirect('detail_question', question_id=question_id)


def round_up_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.FINISHED_QUESTION
    question.save()
    return redirect('detail_question', question_id=question_id)


def revoke_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.REVOKED_QUESTION
    question.save()
    return redirect('detail_question', question_id=question_id)


def deny_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.DENIED_QUESTION
    question.save()
    return redirect('detail_question', question_id=question_id)


def open_question(request, question_id):
    question = Question.objects.get(id=question_id)

    question.state = Question.PUBLIC_QUESTION
    question.student = None

    for region in request.user.as_manager().region.all():
        question.region_processing.remove(region)

    question.save()
    return redirect('detail_question', question_id=question_id)


def distribute_intake(request, question_id):
    question = Question.objects.get(id=question_id)

    print(request.POST)
    region = Region.objects.get(region=request.POST.getlist('region')[0])
    question.region.add(region)
    question.state = Question.INTAKE_QUESTION
    question.save()

    return redirect('detail_question', question_id=int(question_id))


def internal_remark(request, question_id):
    question = Question.objects.get(id=question_id)

    if request.method == 'POST':
        form = InternalRemarkForm(request.POST)
        if form.is_valid():
            new_remark = form.cleaned_data['internal_remark']
            question.internal_remarks = new_remark
            question.save()
            return redirect('detail_question', question_id=question_id)

    else:
        existing_remark = question.internal_remarks
        data = {'internal_remark': existing_remark}
        form = InternalRemarkForm(initial=data)

    return render(request, 'dbwwinkel/question_detail/internal_remark.html', {'form': form, 'question_id': question_id})


def finish_intake(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.IN_PROGRESS_QUESTION_CENTRAL
    question.save()
    return redirect('detail_question', question_id=int(question_id))


def distribute_to_public(request, question_id):
    question = Question.objects.get(id=question_id)
    print(request.POST)
    if request.POST.getlist('region', False):
        regions = request.POST.getlist('region', False)
        region = Region.objects.filter(region__in=regions)
        question.region.set(region)
        question.region_processing.set(region)
        question.state = question.IN_PROGRESS_QUESTION_REGIONAL
        question.save()

    return redirect('detail_question', question_id=int(question_id))


def interested_in_question_view(request, question_id):
    # if this is a POST request we need to process the form data
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StudentForm(request.POST, prefix='student')
        address_form = AdressForm(request.POST, prefix='address')
        # check whether it's valid:
        if form.is_valid() and address_form.is_valid():
            student = form.save(commit=False)
            address = address_form.save()

            student.address = address
            student.save()
            question.potential_students.add(student)
            question.save()

            return render(request, 'dbwwinkel/templates/confirmations/student_choose_success.html',
                          {'question': question})


    # if a GET (or any other method) we'll create a blank form
    else:
        form = StudentForm(prefix='student')
        address_form = AdressForm(prefix='address')

    form.fields['education'].queryset = question.education.all()

    context = {'form': form,
               'question': question,
               'address_form': address_form,
               }
    print(address_form.errors)
    return render(request, 'dbwwinkel/templates/forms_creation/student_form.html', context)


def edit_meta_info(request, question_id):
    # if this is a POST request we need to process the form data
    question = Question.objects.get(id=question_id)
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = MetaFieldForm(request.POST, question_id=question_id)

        # check whether it's valid:
        if form.is_valid():

            for field in form.cleaned_data['institution_delete']:
                question.remove_institution(field)

            for field in form.cleaned_data['institution']:
                question.institution.add(field)

            for field in form.cleaned_data['promotor_delete']:
                field.question_set.remove(question)
                question.promotor.remove(field)
                field.save()
                question.save()

            for field in form.cleaned_data['promotor']:
                question.promotor.add(field)

            for field in form.cleaned_data['faculty_delete']:
                field.question_set.remove(question)
                question.remove_faculty(field)
                field.save()
                question.save()

            for field in form.cleaned_data['faculty']:
                question.faculty.add(field)

            new_one = form.cleaned_data['faculty_new']
            if new_one != '':
                if Faculty.objects.filter(name=new_one).exists():
                    fac = Faculty.objects.get(name=new_one)
                    for inst in question.institution.all():
                        f1 = FacultyOf.objects.create(institution=inst, faculty=fac)
                        f1.save()
                    question.faculty.add(fac)
                    question.save()
                else:
                    new_fac_field = Faculty.objects.create(name=new_one)

                    for inst in question.institution.all():
                        f1 = FacultyOf.objects.create(institution=inst, faculty=new_fac_field)
                        f1.save()
                    new_fac_field.save()
                    question.faculty.add(new_fac_field)
                    new_fac_field.save()

            for field in form.cleaned_data['education_delete']:
                field.question_set.remove(question)
                question.remove_education(field)
                field.save()
                question.save()

            new_one = form.cleaned_data['education_new']
            if new_one != '':
                if Education.objects.filter(education=new_one).exists():
                    educ = Education.objects.get(education=new_one)
                    for inst in question.institution.all():
                        for fac in question.faculty.all():
                            if FacultyOf.objects.filter(institution=inst, faculty=fac).exists():
                                fac_of = FacultyOf.objects.get(institution=inst, faculty=fac)
                                fac_of.education.add(educ)
                                fac_of.save()
                                question.education.add(educ)
                                question.save()
                else:

                    new_st_field = Education(education=new_one)
                    new_st_field.save()

                    for inst in question.institution.all():
                        for fac in question.faculty.all():
                            if FacultyOf.objects.filter(institution=inst, faculty=fac).exists():
                                fac_of = FacultyOf.objects.get(institution=inst, faculty=fac)
                                fac_of.education.add(new_st_field)
                                fac_of.save()
                    question.education.add(new_st_field)

            for field in form.cleaned_data["education"]:
                question.education.add(field)

            new_one = form.cleaned_data['subject_new']
            if new_one != '':
                new_q_field = QuestionSubject(subject=new_one)
                new_q_field.save()
                question.question_subject.add(new_q_field)

            for field in form.cleaned_data['subject_delete']:
                field.question_set.remove(question)
                question.question_subject.remove(field)
                field.save()

            for field in form.cleaned_data['subject']:
                question.question_subject.add(field)

            question.save()
            form = MetaFieldForm(question_id=question_id)
            return render(request, 'dbwwinkel/question_detail/edit_meta_data.html',
                          {'form': form, 'question': question})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MetaFieldForm(question_id=question_id)

    return render(request, 'dbwwinkel/question_detail/edit_meta_data.html', {'form': form, 'question': question})


def register_institution(request, question_id):
    if request.method == 'POST':
        institution_form = InstitutionForm(request.POST, prefix='institution')
        address_form = AdressForm(request.POST, prefix='address')

        if institution_form.is_valid() and address_form.is_valid():
            institution = institution_form.save(commit=False)
            address = address_form.save()

            institution.address = address
            institution.save()

            question = Question.objects.get(id=question_id)
            question.institution.add(institution)
            question.save()

            return redirect('edit_meta_info', question_id=question_id)
    else:
        institution_form = InstitutionForm(prefix='institution')
        address_form = AdressForm(prefix='address')

    context = {
        'institution_form': institution_form,
        'address_form': address_form,
        'question_id': question_id
    }
    return render(request, 'dbwwinkel/templates/forms_creation/create_institution.html', context)


def register_promotor(request, question_id):
    if request.method == 'POST':
        promotor_form = PromotorForm(request.POST)

        if promotor_form.is_valid():
            promotor = promotor_form.save(commit=False)

            promotor.address = promotor.institution.address
            promotor.save()

            question = Question.objects.get(id=question_id)
            question.promotor.add(promotor)
            question.save()

            return redirect('edit_meta_info', question_id=question_id)
    else:
        promotor_form = PromotorForm()

    context = {
        'promotor_form': promotor_form,
        'question_id': question_id
    }
    return render(request, 'dbwwinkel/templates/forms_creation/create_promotor.html', context)


def administration_view_to_process(request):
    # 2 Kinds of admin users, centrals want in_progress central and new questions
    sqs = Question.objects.none()

    if request.user.is_regional_manager():
        region_lst = request.user.as_manager().region.all()
        sqs = Question.objects.filter(region__in=region_lst)
        sqs = sqs.filter(state__in=[Question.IN_PROGRESS_QUESTION_REGIONAL, Question.INTAKE_QUESTION])

        sqs2 = Question.objects.filter(state=Question.PUBLIC_QUESTION)
        sqs = sqs | sqs2.filter(region_processing__in=region_lst)

        sqs = sqs | sqs2.filter(region__in=region_lst).exclude(potential_students=None)

        sqs2 = Question.objects.filter(state=Question.RESERVED_QUESTION)
        sqs = sqs | sqs2.filter(region__in=region_lst)

    if request.user.is_central_manager():
        sqs = sqs | Question.objects.filter(state__in=[Question.NEW_QUESTION, Question.IN_PROGRESS_QUESTION_CENTRAL])

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_new(request):
    sqs = Question.objects.filter(state=Question.NEW_QUESTION)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_intake_process(request):
    if request.user.is_regional_manager():
        region_lst = request.user.as_manager().region.all()
        sqs = Question.objects.filter(region__in=region_lst)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_intake_in_progress(request):
    sqs = Question.objects.none()
    if request.user.is_manager:
        sqs = Question.objects.filter(state=Question.IN_PROGRESS_QUESTION_REGIONAL)

        region_lst = request.user.as_manager().region.all()
        sqs = sqs.filter(region__in=region_lst)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_intake_done(request):
    sqs = Question.objects.filter(state=Question.IN_PROGRESS_QUESTION_CENTRAL)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_in_regional_process(request):
    sqs = Question.objects.filter(state=Question.IN_PROGRESS_QUESTION_REGIONAL)

    region_lst = request.user.as_manager().region.all()
    sqs = sqs.filter(region__in=region_lst)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_in_regional_process_all(request):
    sqs = Question.objects.filter(state=Question.IN_PROGRESS_QUESTION_REGIONAL)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_public(request):
    sqs = Question.objects.filter(state=Question.PUBLIC_QUESTION)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_reserved(request):
    sqs = Question.objects.filter(state=Question.RESERVED_QUESTION)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_on_going(request):
    sqs = Question.objects.filter(state=Question.ONGOING_QUESTION)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_finished(request):
    sqs = Question.objects.filter(state=Question.FINISHED_QUESTION)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_denied(request):
    sqs = Question.objects.filter(state=Question.DENIED_QUESTION)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_revoked(request):
    sqs = Question.objects.filter(state=Question.REVOKED_QUESTION)

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def administration_view_my_questions(request):
    sqs = Question.objects.filter(region__in=request.user.as_manager().region.all())

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_page.html', context)


def admin_organisation_table_view(request):
    sqs = Organisation.objects.all()

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_organisations.html', context)


def admin_organisation_contact_view(request):
    sqs = OrganisationUser.objects.all()

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_contacts.html', context)


def admin_institution_view(request):
    sqs = Institution.objects.all()

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_institution.html', context)


def admin_faculty_view(request):
    sqs = Faculty.objects.all()

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_faculty.html', context)


def admin_education_view(request):
    sqs = Education.objects.all()

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_education.html', context)


def admin_promotor_view(request):
    sqs = Promotor.objects.all()

    context = {
        'query': sqs
    }
    return render(request, 'dbwwinkel/admin/admin_promotor.html', context)


class OrganisationDetail(DetailView):
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetail, self).get_context_data(**kwargs)
        return context


class InstitutionDetail(DetailView):
    model = Institution

    def get_context_data(self, **kwargs):
        context = super(InstitutionDetail, self).get_context_data(**kwargs)
        return context


class FacultyDetail(DetailView):
    model = Faculty

    def get_context_data(self, **kwargs):
        context = super(FacultyDetail, self).get_context_data(**kwargs)
        return context


class EducationDetail(DetailView):
    model = Education

    def get_context_data(self, **kwargs):
        context = super(EducationDetail, self).get_context_data(**kwargs)
        return context

class ContactDetail(DetailView):
    model = OrganisationUser

    template_name = 'dbwwinkel/contact_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ContactDetail, self).get_context_data(**kwargs)
        return context
