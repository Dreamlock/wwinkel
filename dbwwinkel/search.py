from .models import Question
from haystack.query import SearchQuerySet


def autocomplete(query, value, object = Question):
    """Handles autocomplete logic for searching"""

    if value == '':
        return query

    return query.autocomplete(content_auto=value)


def query_on_facets(start_query, dictionary):
    pass


def query_extra_content(user,start_query):

    # a organisation_user wants to see his own questions
    if user.is_organisation():
        return start_query | SearchQuerySet().filter(organisation = user.as_organisation().organisation.id)

    # The regionals want the questions assigned to them
    elif user.is_manager() and user.is_regional_manager():
        return start_query | SearchQuerySet().filter(
            region__in=[region.region for region in user.as_manager().region.all()])

    return start_query

def query_on_states(start_query, states):

    return start_query.filter(state__in = states)