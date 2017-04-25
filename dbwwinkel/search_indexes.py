import datetime
from haystack import indexes
from dbwwinkel.models import Question


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    study_field = indexes.FacetMultiValueField()
    content_auto = indexes.EdgeNgramField(model_attr='question_text')

    state = indexes.CharField(model_attr='state__state')
    organisation = indexes.CharField(model_attr ='organisation__id' )


    def prepare_study_field(self, obj):
        return [l.study_field for l in obj.study_field.all()]

    def get_model(self):
        return Question
