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
    # We will start filtering from here

    sqs = SearchQuerySet().all().models(Question)
    facet_form = FacetForm(request.GET)

    if not facet_form.is_valid():

        return HttpResponse("Dit is een probleem")
    print(request.GET)
    status_lst = Question.STATE_SELECT
    # we filter all questions that are not public, reserved, or finished, we don't do this for the central maanger
    if not request.user.is_authenticated() or not request.user.is_central_manager():
        status_lst = [
            status_lst[Question.PUBLIC_QUESTION],
            status_lst[Question.RESERVED_QUESTION],
            status_lst[Question.FINISHED_QUESTION]
        ]
        sqs = sqs.filter(state__in=[status[0] for status in status_lst])

        facet_form.fields['status'].choices = status_lst

    # Filter out the status of questions needed
    if facet_form.cleaned_data['status']:
        data = facet_form.cleaned_data['status']
        facet_form.fields['status'].initial = list(map(int, data))
        sqs = query_on_states(sqs, data)

    # Check if some extra questions need to be added to the queryset
    if facet_form.cleaned_data['own_questions']:
        sqs = query_extra_content(request.user, sqs)

    # Text based search, now we're set up for our facets
    val = request.GET.get('search_text', '')
    sqs = search(sqs, val, Question)

    sqs = sqs.facet('institution_facet')
    choice_institution = sqs.facet_counts()['fields']['institution_facet']
    facet_form.fields['institution'].choices = choice_institution
    if facet_form.cleaned_data['institution']:
        sqs = sqs.filter(institution_facet__in = facet_form.cleaned_data['institution'])
        facet_form.fields['institution'].initial = list(map(str, facet_form.cleaned_data['institution']))


    context = {'questions': sqs,
               'facet_form': facet_form,
               'search_text': val,
               }

    return render(request, 'dbwwinkel/question_list.html', context)


def l_questions(request):
    val = request.GET.get('search_text', '')
    sqs = search(SearchQuerySet().all().models(Question), val, Question)
    # States visible for everyone
    visible_states = [Question.STATE_SELECT[Question.PUBLIC_QUESTION], Question.STATE_SELECT[Question.RESERVED_QUESTION]
        , Question.STATE_SELECT[Question.FINISHED_QUESTION]]

    # Fetching all the data specified on user
    if request.user.is_authenticated():
        if request.user.is_organisation():
            user = OrganisationUser.objects.get(id=request.user.id)
            organisation = user.organisation
            organisation_extra = SearchQuerySet().filter(
                organisation=organisation.id)  # the organisations own questions


        elif request.user.is_manager():

            user = ManagerUser.objects.get(id=request.user.id)

            if user.region.filter(region=Region.CENTRAL_REGION).exists():
                visible_states = Question.STATE_SELECT

            else:
                regional_extra = SearchQuerySet().filter(region__in=[region.region for region in user.region.all()])

    if request.POST:  # start filtering
        sqs = sqs.filter(state__in=request.POST.getlist("status"))

        if OrganisationUser.objects.filter(id=request.user.id).exists():
            if request.POST.getlist('own_question'):
                sqs = sqs | organisation_extra

        if request.user.is_authenticated and request.user.is_manager():
            user = ManagerUser.objects.get(id=request.user.id)
            if not user.region.filter(region=Region.CENTRAL_REGION).exists():
                if request.POST.getlist('own_question'):
                    sqs = sqs | regional_extra

        if request.POST.getlist("education"):
            sqs = sqs.filter(education_facet__in=request.POST.getlist("education"))


    else:
        if request.user.is_authenticated():
            if request.user.is_organisation():
                organisation_extra = search(organisation_extra, val, Question)
                sqs = sqs.filter(state__in=[l[0] for l in visible_states]) | organisation_extra

            elif request.user.is_manager():

                user = ManagerUser.objects.get(id=request.user.id)

                if user.region.filter(region=Region.CENTRAL_REGION).exists():  # No extra filters to apply
                    pass

                else:  # + the extra ones bound to this region
                    regional_extra = search(regional_extra, val, Question)
                    sqs = sqs | regional_extra

        else:  # is student
            sqs = sqs.filter(state__in=[l[0] for l in visible_states])

    own_question = False
    if request.user.is_authenticated() and request.user.is_organisation():
        own_question = True

    if request.user.is_authenticated and request.user.is_manager():
        user = ManagerUser.objects.get(id=request.user.id)
        if not user.region.filter(region=Region.CENTRAL_REGION).exists():
            own_question = True

    true_states = []
    for state in visible_states:
        tuple = (state[0], state[1], True)
        true_states.append(tuple)

    context = {'questions': sqs,
               'states': true_states,
               # 'educations': education,
               'search_text': val,
               'own_question': own_question
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
