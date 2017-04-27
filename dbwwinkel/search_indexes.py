import datetime
from haystack import indexes
from dbwwinkel.models import Question


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    content_auto = indexes.EdgeNgramField(model_attr='question_text')

    state = indexes.CharField(model_attr='state__state')
    region = indexes.CharField()
    study_field = indexes.CharField()
    organisation = indexes.CharField(model_attr ='organisation__id' )

    #Facets
    study_field_facet = indexes.FacetMultiValueField()

    def prepare_region(self, obj):
        return [region.region for region in obj.region.all()]

    def prepare_study_field(self,obj):
        return [l.study_field for l in obj.study_field.all()]

    def prepare_study_field_facet(self, obj):
        return [l.study_field for l in obj.study_field.all()]

    def get_model(self):
        return Question
