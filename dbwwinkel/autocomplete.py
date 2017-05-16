from dal import autocomplete as lightcomplete
from .models import Education, QuestionSubject, Institution, Promotor, Question, Faculty, FacultyOf
from django.db.models import Q


class InstitutionAutocomplete(lightcomplete.Select2QuerySetView):
    def get_queryset(self):
        question_id = self.forwarded.get('question_id', None)
        question = Question.objects.get(id=question_id)
        qs = Institution.objects.exclude(id__in=[inst.id for inst in question.institution.all()])
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class PromotorAutocomplete(lightcomplete.Select2QuerySetView):
    def get_queryset(self):
        question_id = self.forwarded.get('question_id', None)
        question = Question.objects.get(id=question_id)
        new_lst = self.forwarded.get('institution')

        real_time_institutions = Institution.objects.filter(id__in=new_lst)

        real_proms = Promotor.objects.none()
        for inst in real_time_institutions:
            real_proms = real_proms | inst.promotor_set.all()

        qs = (question.possible_promotors | real_proms).exclude(
            id__in=[promotor.id for promotor in question.promotor.all()])
        if self.q:
            qs = qs.filter(Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q))

        return qs


class FacultyAutocomplete(lightcomplete.Select2QuerySetView):
    def get_queryset(self):

        question_id = self.forwarded.get('question_id', None)
        question = Question.objects.get(id=question_id)
        new_lst = self.forwarded.get('institution')

        real_time_institutions = Institution.objects.filter(id__in=new_lst)

        real_faculty = Faculty.objects.none()
        for inst in real_time_institutions:
            real_faculty = real_faculty | inst.faculty_set.all()

        qs = (question.possible_faculty | real_faculty).exclude(
            id__in=[faculty.id for faculty in question.faculty.all()])
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class EducationAutocomplete(lightcomplete.Select2QuerySetView):

    def get_queryset(self):
        question_id = self.forwarded.get('question_id', None)
        question = Question.objects.get(id=question_id)
        new_lst = self.forwarded.get('faculty')
        new_lst_inst = self.forwarded.get('institution')
        real_time_faculties = Faculty.objects.filter(id__in=new_lst) | question.faculty.all()
        real_time_inst = Institution.objects.filter(id__in=new_lst_inst) | question.institution.all()

        real_education = Education.objects.none()
        for fac in real_time_faculties:
            for inst in real_time_inst:
                if FacultyOf.objects.filter(faculty=fac, institution=inst).exists():
                    fac_of = FacultyOf.objects.get(faculty=fac, institution=inst)
                    real_education = real_education | fac_of.education.all()

        qs = ((real_education | question.possible_education).distinct()).exclude(
            id__in = [education.id for education in question.education.all()])
        if self.q:
            qs = qs.filter(education__istartswith=self.q)

        return qs


class SubjectAutocomplete(lightcomplete.Select2QuerySetView):

    def get_queryset(self):

        question_id = self.forwarded.get('question_id', None)
        print(question_id)
        question = Question.objects.get(id=question_id)
        new_lst = self.forwarded.get('education')
        real_time_educations = Education.objects.filter(id__in=new_lst)

        real_subject = QuestionSubject.objects.none()
        for edu in real_time_educations:
            real_education = real_education | edu.questionsubject_set.all()

        qs = (question.possible_subject | real_subject).exclude(
            id__in=[subject.id for subject in question.question_subject.all()])
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

