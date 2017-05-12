from dal import autocomplete as lightcomplete
from .models import Education, QuestionSubject, Institution, Promotor, Question, Faculty
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

        qs = Faculty.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class EducationAutocomplete(lightcomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Education.objects.all()
        if self.q:
            qs = qs.filter(education__istartswith=self.q)

        return qs


class SubjectAutocomplete(lightcomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        qs = QuestionSubject.objects.all()
        if self.q:
            qs = qs.filter(subject__istartswith=self.q)

        return qs
