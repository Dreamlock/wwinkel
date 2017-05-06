from .models import Question
from haystack.query import SearchQuerySet


def autocomplete(list, value, object = Question):
    """Handles autocomplete logic for searching"""

    if value == '':
        return list.all().models(object)

    return list.autocomplete(content_auto=value)
