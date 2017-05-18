from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from haystack.query import SearchQuerySet

from custom_users.forms import AdressForm
from .forms import *
from .models import Question, Education, QuestionSubject, FacultyOf
from custom_users.models import OrganisationUser, ManagerUser, Region
from operator import itemgetter
from .search import autocomplete as search, query_extra_content, query_on_states


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
    # Text based search, now we're set up for our facets
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


    # Filter out the status of questions needed
    if facet_form.data.get('status', False):
        data = facet_form.data['status']
        facet_form.fields['status'].initial = list(map(int, data))
        sqs = query_on_states(sqs, data)

    # Check if some extra questions need to be added to the queryset
    if facet_form.data.get('own_questions', False):
        sqs = query_extra_content(request.user, sqs)

    # Filter based on Facets
    field_lst = ['institution', 'faculty', 'education', 'subject', 'promotor']
    for field in field_lst:
        facet_data = facet_form.data.getlist(field, False)
        if facet_data:
            sqs = sqs.filter(**{'{0}_facet__in'.format(field):facet_data})
            facet_form.fields[field].initial = list(map(str, facet_data))

    # Calculate the facets
    facet_count = [None, None]
    for field in field_lst:
        sqs = sqs.facet('{0}_facet'.format(field), mincount=1, limit=5)
        choice_facet = (sqs.facet_counts()['fields']['{0}_facet'.format(field)])
        choice_facet = sorted(choice_facet,reverse = True, key =itemgetter(1))
        helper_lst = []
        for choice in choice_facet:
            helper_lst.append((choice[0], choice[0]))
        facet_form.fields[field].choices = helper_lst
        facet_count.append(choice_facet)


    context = {'questions': sqs,
               'facet_form': facet_form,
               'search_text': val,
               'facet_count': facet_count
               }

    return render(request, 'dbwwinkel/question_list.html', context)


def detail(request, question_id):
    question = Question.objects.get(id=question_id)
    organisation = question.organisation

    if request.user.is_authenticated == False:  # Then the user is a student
        return student_detail(request, question, organisation)

    elif OrganisationUser.objects.filter(id=request.user.id).exists():
        organisation = (OrganisationUser.objects.get(id=request.user.id)).organisation
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

    return render(request, 'dbwwinkel/detail_question/regional_unit.html', context)


def central_detail(request, question, organisation):
    region_list = []
    for region in Region.objects.all():
        if region.region != Region.CENTRAL_REGION:
            region_list.append((region, region.region))
    context = {'question': question,
               'region_lst': region_list,
               'organisation': organisation,
               'internal': True}
    return render(request, 'dbwwinkel/detail_question/central_unit.html', context)


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
        return redirect(detail, question_id=question_id)
    return render(request, 'dbwwinkel/vraagstelform.html', {'form': form})


def reserve_question(request, question_id):
    question = Question.objects.get(id=question_id)
    if request.user.is_authenticated == False and question.state.state == Question.PUBLIC_QUESTION:
        add = ""
        for region in question.region.all():
            add += "{0} ".format(region)
        question.state = Question.RESERVED_QUESTION
        question.save()
        return HttpResponse("Vraag gereserveerd."
                            "\nGelieve contact op te nemen met de medewerker(s) van: {0}".format(add))


def distribute_question(request, question_id):
    question = Question.objects.get(id=question_id)

    for region in request.POST.getlist('region'):
        region_obj = Region.objects.get(region=region)
        question.region.add(region_obj)

    question.state = Question.IN_PROGRESS_QUESTION_REGIONAL
    question.save()

    return HttpResponse("Toegewezen")


def open_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.PUBLIC_QUESTION
    question.save()
    return HttpResponse("Vraag staat publiek")


def assign_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.ONGOING_QUESTION
    question.save()
    return HttpResponse("Vraag is nu lopend")


def round_up_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.FINISHED_QUESTION
    question.save()
    return HttpResponse("Vraag is afgerond")


def deny_question(request, question_id):
    """FAKE NEWS"""

    question = Question.objects.get(id=question_id)
    question.state = Question.DENIED_QUESTION
    question.save()
    return HttpResponse("Vraag is geweigerd")


def revoke_question(request, question_id):
    question = Question.objects.get(id=question_id)
    question.state = Question.REVOKED_QUESTION
    question.save()
    return HttpResponse("Vraag is terug getrokken")


def distribute_intake(request, question_id):
    question = Question.objects.get(id=question_id)

    region = Region.objects.get(region=request.POST.getlist('region')[0])
    question.region.add(region)
    question.state = Question.IN_PROGRESS_QUESTION_REGIONAL
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

    return render(request, 'dbwwinkel/internal_remark.html', {'form': form, 'question_id': question_id})


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
            return render(request, 'dbwwinkel/edit_meta_data.html', {'form': form, 'question': question})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MetaFieldForm(question_id=question_id)

    return render(request, 'dbwwinkel/edit_meta_data.html', {'form': form, 'question': question})


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
    return render(request, 'dbwwinkel/create_institution.html', context)


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
    return render(request, 'dbwwinkel/create_promotor.html', context)
