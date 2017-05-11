from django.utils.translation import ugettext_lazy as _
from dbwwinkel.models import Question
from custom_users.models import User, OrganisationUser, ManagerUser

# get all fields: [f.name for f in Question._meta.get_fields()]


def get_next_state(current_state):
    state_transition = {
        Question.DRAFT_QUESTION: {
            Question.NEW_QUESTION,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.NEW_QUESTION: {
            Question.INTAKE_QUESTION,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.INTAKE_QUESTION: {
            Question.IN_PROGRESS_QUESTION_CENTRAL,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.IN_PROGRESS_QUESTION_CENTRAL: {
            Question.PROCESSED_QUESTION_CENTRAL,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.PROCESSED_QUESTION_CENTRAL: {
            Question.IN_PROGRESS_QUESTION_REGIONAL,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.IN_PROGRESS_QUESTION_REGIONAL: {
            Question.PUBLIC_QUESTION,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.PUBLIC_QUESTION: {
            Question.RESERVED_QUESTION,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.RESERVED_QUESTION: {
            Question.ONGOING_QUESTION,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.ONGOING_QUESTION: {
            Question.FINISHED_QUESTION,
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.FINISHED_QUESTION: {
            Question.DENIED_QUESTION,
            Question.REVOKED_QUESTION
        },
        Question.DENIED_QUESTION: set(),
        Question.REVOKED_QUESTION: set(),
    }
    return state_transition[current_state]


def get_viewable_states_student():
    return {
        Question.PUBLIC_QUESTION,
        Question.RESERVED_QUESTION,
        Question.FINISHED_QUESTION,
    }


def get_viewable_fields_student(question):
    result = set()
    if question.public:
        result = {
            'question_text',
            'reason',
            'purpose',
            'remarks',
            'deadline',
            'state',
            'organisation',
            'question_subject',
            'education',
        }
        if question.state == Question.FINISHED_QUESTION:
            result |= {'student', 'completion_date'}
    return result


def get_viewable_states_organisation():
    return {
        state[0] for state in Question.STATE_SELECT  # every state
        }


def get_viewable_fields_organisation(question):
    result = {
        'question_text',
        'reason',
        'purpose',
        'own_contribution',
        'remarks',
        'deadline',
        'public',
        'creation_date',
        'state',
        'organisation',
        'keyword',
        'question_subject',
        'education',
    }
    if question.state == Question.ONGOING_QUESTION:
        result |= {'student'}
    if question.state == Question.FINISHED_QUESTION:
        result |= {'student', 'completion_date'}
    return result


def get_viewable_states_central_manager():
    return {
        Question.DRAFT_QUESTION,
        Question.NEW_QUESTION,
        Question.IN_PROGRESS_QUESTION_CENTRAL,
        Question.PROCESSED_QUESTION_CENTRAL,
        Question.PUBLIC_QUESTION,
        Question.RESERVED_QUESTION,
        Question.FINISHED_QUESTION,
    }


def get_viewable_fields_central_manager(question):
    result = {
        'question_text',
        'reason',
        'purpose',
        'own_contribution',
        'remarks',
        'deadline',
        'public',
        'creation_date',
        'state',
        'organisation',
        'region',
        'keyword',
        'question_subject',
        'education',
    }
    if question.state == Question.ONGOING_QUESTION:
        result |= {'student'}
    if question.state == Question.FINISHED_QUESTION:
        result |= {'student', 'completion_date'}
    return result


def get_viewable_states_regional_manager():
    return {
        Question.INTAKE_QUESTION,
        Question.IN_PROGRESS_QUESTION_REGIONAL,
        Question.PUBLIC_QUESTION,
        Question.RESERVED_QUESTION,
        Question.FINISHED_QUESTION,
    }


def get_viewable_fields_regional_manager(question):
    result = {
        'question_text',
        'reason',
        'purpose',
        'own_contribution',
        'remarks',
        'deadline',
        'public',
        'creation_date',
        'state',
        'organisation',
        'region',
        'keyword',
        'question_subject',
        'education',
    }
    if question.state == Question.ONGOING_QUESTION:
        result |= {'student'}
    if question.state == Question.FINISHED_QUESTION:
        result |= {'student', 'completion_date'}
    return result


def get_editable_states_student():
    return set()


def get_editable_fields_student(question):
    return set()


def get_editable_states_organisation():
    return {
        Question.DRAFT_QUESTION,
    }


def get_editable_fields_organisation(question):
    result = get_viewable_fields_organisation(question)
    result -= {
        'creation_date',
        'state',
    }
    return result


def get_editable_states_central_manager():
    return {
        Question.DRAFT_QUESTION,
        Question.NEW_QUESTION,
        Question.IN_PROGRESS_QUESTION_CENTRAL,
        Question.PROCESSED_QUESTION_CENTRAL,
    }


def get_editable_fields_central_manager(question):
    if question.state == Question.DRAFT_QUESTION:
        result = {'state'}
    else:
        result = {
            'question_text',
            'reason',
            'purpose',
            'own_contribution',
            'remarks',
            'deadline',
            'public',
            'state',
            'organisation',
            'region',
            'keyword',
            'question_subject',
            'education',
        }
    return result


def get_editable_states_regional_manager():
    return {
        Question.INTAKE_QUESTION,
        Question.IN_PROGRESS_QUESTION_REGIONAL,
        Question.PUBLIC_QUESTION,
        Question.RESERVED_QUESTION,
        Question.FINISHED_QUESTION,
    }


def get_editable_fields_regional_manager(question):
    result = {
        'question_text',
        'reason',
        'purpose',
        'own_contribution',
        'remarks',
        'deadline',
        'public',
        'state',
        'organisation',
        'keyword',
        'question_subject',
        'education',
    }
    if question.state == Question.ONGOING_QUESTION:
        result |= {'student'}
    if question.state == Question.FINISHED_QUESTION:
        result |= {'student', 'completion_date'}
    return result


def get_viewable_states(user):
    result = get_viewable_states_student()
    if user.is_organisation():
        result |= get_viewable_states_organisation()
    if user.is_manager():
        user = user.as_manager()
        if user.is_central_manager():
            result |= get_viewable_states_central_manager()
        if user.is_regional_manager():
            result |= get_viewable_states_regional_manager()
    return result


def get_editable_states(user):
    result = get_editable_states_student()
    if user.is_organisation():
        result |= get_editable_states_organisation()
    if user.is_manager():
        user = user.as_manager()
        if user.is_central_manager():
            result |= get_editable_states_central_manager()
        if user.is_regional_manager():
            result |= get_editable_states_regional_manager()
    return result


def get_viewable_fields(user, question):
    result = set()
    if question.state in get_viewable_states(user):
        result = get_viewable_fields_student(question)
        if user.is_organisation():
            result |= get_viewable_fields_organisation(question)
        if user.is_manager():
            user = user.as_manager()
            if user.is_central_manager():
                result |= get_viewable_fields_central_manager(question)
            if user.is_regional_manager():
                result |= get_viewable_fields_regional_manager(question)
    return result


def get_editable_fields(user, question):
    result = set()
    if question.state in get_editable_states(user):
        result = get_editable_fields_student(question)
        if user.is_organisation():
            result |= get_editable_fields_organisation(question)
        if user.is_manager():
            user = user.as_manager()
            if user.is_central_manager():
                result |= get_editable_fields_central_manager(question)
            if user.is_regional_manager():
                result |= get_editable_fields_regional_manager(question)
    return result
