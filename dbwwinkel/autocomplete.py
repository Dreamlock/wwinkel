from dal import autocomplete as lightcomplete
from .models import Education, QuestionSubject, Institution



class InstitutionAutocomplete(lightcomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        qs = Institution.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class EducationAutocomplete(lightcomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
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
