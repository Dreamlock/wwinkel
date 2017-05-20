import datetime
from haystack import indexes
from dbwwinkel.models import Question


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    content_auto = indexes.EdgeNgramField(model_attr='question_text')

    state = indexes.IntegerField(model_attr='state')
    region = indexes.MultiValueField()
    organisation = indexes.CharField(model_attr='organisation__id')

    #Facets
    state_facet = indexes.FacetIntegerField(model_attr = 'state')
    institution_facet = indexes.FacetMultiValueField()
    promotor_facet = indexes.FacetMultiValueField()
    faculty_facet = indexes.FacetMultiValueField()
    education_facet = indexes.FacetMultiValueField()
    subject_facet = indexes.FacetMultiValueField()
    key_word_facet = indexes.FacetMultiValueField()


    def prepare_region(self, obj):
        return [region.region for region in obj.region.all()]

    def prepare_institution_facet(self,obj):
        return [institution.name for institution in obj.institution.all()]

    def prepare_promotor_facet(self,obj):
        return ['{0} {1}'.format(promotor.first_name, promotor.last_name) for promotor in obj.promotor.all()]

    def prepare_faculty_facet(self,obj):
        return [faculty.name for faculty in obj.faculty.all()]

    def prepare_education_facet(self, obj):
        return [education.education for education in obj.education.all()]

    def prepare_subject_facet(self,obj):
        return [subject.subject for subject in obj.question_subject.all()]

    def prepare_key_word_facet(self,obj):
        return [keyword.key_word for keyword in obj.keyword.all()]

    def get_model(self):
        return Question
