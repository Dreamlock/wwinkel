import datetime
from haystack import indexes
from dbwwinkel.models import Question


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    content_auto = indexes.EdgeNgramField(model_attr='question_text')

    state = indexes.IntegerField(model_attr='state')
    region = indexes.MultiValueField()
    organisation = indexes.CharField(model_attr='organisation__id')

    # Facets
    # education_facet = indexes.FacetMultiValueField()

    def prepare_region(self, obj):
        return [region.region for region in obj.region.all()]

    def get_model(self):
        return Question
