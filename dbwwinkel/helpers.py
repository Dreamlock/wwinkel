from django.utils.translation import ugettext_lazy as _
from dbwwinkel.models import Question
from custom_users.models import User, OrganisationUser, ManagerUser

class StateIndex:
    state_names = (
        'draft', 'in_progress_central', 'processed_central', 'in_progress_regional'
    )

    DRAFT_QUESTION = 0
    NEW_QUESTION = 1
    INTAKE_QUESTION = 2
    IN_PROGRESS_QUESTION_CENTRAL = 3
    PROCESSED_QUESTION_CENTRAL = 4
    IN_PROGRESS_QUESTION_REGIONAL = 5
    PUBLIC_QUESTION = 6
    RESERVED_QUESTION = 7
    ONGOING_QUESTION = 8
    FINISHED_QUESTION = 9
    DENIED_QUESTION = 10
    REVOKED_QUESTION = 11

    STATE_SELECT = (
        (DRAFT_QUESTION, _('draft')),
        (NEW_QUESTION, _('new')),
        (INTAKE_QUESTION, _('intake')),
        (IN_PROGRESS_QUESTION_CENTRAL, _('in progress central')),
        (PROCESSED_QUESTION_CENTRAL, _('processed central')),
        (IN_PROGRESS_QUESTION_REGIONAL, _('in progress regional')),
        (PUBLIC_QUESTION, _('public')),
        (RESERVED_QUESTION, _('reserved')),
        (ONGOING_QUESTION, _('ongoing')),
        (FINISHED_QUESTION, _('finished')),
        (DENIED_QUESTION, _('denied')),
        (REVOKED_QUESTION, _('revoked')),
    )

    # Usage: next_states = STATE_TRANSITION[current_state]
    STATE_TRANSITION = {
        DRAFT_QUESTION: {NEW_QUESTION, DENIED_QUESTION, REVOKED_QUESTION},
        NEW_QUESTION: {INTAKE_QUESTION, DENIED_QUESTION, REVOKED_QUESTION},
        INTAKE_QUESTION: {IN_PROGRESS_QUESTION_CENTRAL, DENIED_QUESTION, REVOKED_QUESTION},
        IN_PROGRESS_QUESTION_CENTRAL: {PROCESSED_QUESTION_CENTRAL, DENIED_QUESTION, REVOKED_QUESTION},
        PROCESSED_QUESTION_CENTRAL: {IN_PROGRESS_QUESTION_REGIONAL, DENIED_QUESTION, REVOKED_QUESTION},
        IN_PROGRESS_QUESTION_REGIONAL: {PUBLIC_QUESTION, DENIED_QUESTION, REVOKED_QUESTION},
        PUBLIC_QUESTION: {RESERVED_QUESTION, DENIED_QUESTION, REVOKED_QUESTION},
        RESERVED_QUESTION: {ONGOING_QUESTION, DENIED_QUESTION, REVOKED_QUESTION},
        ONGOING_QUESTION: {FINISHED_QUESTION, DENIED_QUESTION, REVOKED_QUESTION},
        FINISHED_QUESTION: {DENIED_QUESTION, REVOKED_QUESTION},
        DENIED_QUESTION: set(),
        REVOKED_QUESTION: set(),
    }

    VIEWABLE_STATES_STUDENT = {
        PUBLIC_QUESTION,
        RESERVED_QUESTION,
        FINISHED_QUESTION,
    }

    def get_viewable_states_student(self):
        return {
            Question.PUBLIC_QUESTION,
            Question.RESERVED_QUESTION,
            Question.FINISHED_QUESTION,
        }

    def get_viewable_fields_student(self, question):
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
                'study_field',
            }
            if question.state == Question.FINISHED_QUESTION:
                result |= {'student', 'completion_date'}
        return result

    def get_viewable_states_organisation(self):
        return {
            state[0] for state in Question.STATE_SELECT  # every state
        }

    def get_viewable_fields_organisation(self, question):
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
            'study_field',
        }
        if question.state == Question.ONGOING_QUESTION:
            result |= {'student'}
        if question.state == Question.FINISHED_QUESTION:
            result |= {'student', 'completion_date'}
        return result

    def get_viewable_states_central_manager(self):
        return {
            Question.DRAFT_QUESTION,
            Question.NEW_QUESTION,
            Question.IN_PROGRESS_QUESTION_CENTRAL,
            Question.PROCESSED_QUESTION_CENTRAL,
            Question.PUBLIC_QUESTION,
            Question.RESERVED_QUESTION,
            Question.FINISHED_QUESTION,
        }

    def get_viewable_fields_central_manager(self, question):
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
            'study_field',
        }
        if question.state == Question.ONGOING_QUESTION:
            result |= {'student'}
        if question.state == Question.FINISHED_QUESTION:
            result |= {'student', 'completion_date'}
        return result

    def get_viewable_states_regional_manager(self):
        return {
            Question.INTAKE_QUESTION,
            Question.IN_PROGRESS_QUESTION_REGIONAL,
            Question.PUBLIC_QUESTION,
            Question.RESERVED_QUESTION,
            Question.FINISHED_QUESTION,
        }

    def get_viewable_fields_regional_manager(self, question):
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
            'study_field',
        }
        if question.state == Question.ONGOING_QUESTION:
            result |= {'student'}
        if question.state == Question.FINISHED_QUESTION:
            result |= {'student', 'completion_date'}
        return result

    def get_editable_states_student(self):
        return set()

    def get_editable_fields_student(self, question):
        return set()

    def get_editable_states_organisation(self):
        return {
            Question.DRAFT_QUESTION,
        }

    def get_editable_fields_organisation(self, question):
        result = self.get_viewable_fields_organisation(question)
        result -= {
            'creation_date',
            'state',
        }
        return result

    def get_editable_states_central_manager(self):
        return {
            Question.DRAFT_QUESTION,
            Question.NEW_QUESTION,
            Question.IN_PROGRESS_QUESTION_CENTRAL,
            Question.PROCESSED_QUESTION_CENTRAL,
        }

    def get_editable_fields_central_manager(self, question):
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
                'study_field',
            }
        return result

    def get_editable_states_regional_manager(self):
        return {
            Question.INTAKE_QUESTION,
            Question.IN_PROGRESS_QUESTION_REGIONAL,
            Question.PUBLIC_QUESTION,
            Question.RESERVED_QUESTION,
            Question.FINISHED_QUESTION,
        }

    def get_editable_fields_regional_manager(self, question):
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
            'study_field',
        }
        if question.state == Question.ONGOING_QUESTION:
            result |= {'student'}
        if question.state == Question.FINISHED_QUESTION:
            result |= {'student', 'completion_date'}
        return result

    def get_viewable_states(self, user):
        result = self.get_viewable_states_student()
        if user.is_organisation():
            result |= self.get_viewable_states_organisation()
        if user.is_manager():
            user = user.as_manager()
            if user.is_central_manager():
                result |= self.get_viewable_states_central_manager()
            if user.is_regional_manager():
                result |= self.get_viewable_states_regional_manager()
        return result
    
    def get_editable_states(self, user):
        result = self.get_editable_states_student()
        if user.is_organisation():
            result |= self.get_editable_states_organisation()
        if user.is_manager():
            user = user.as_manager()
            if user.is_central_manager():
                result |= self.get_editable_states_central_manager()
            if user.is_regional_manager():
                result |= self.get_editable_states_regional_manager()
        return result
    
    def get_viewable_fields(self, user, question):
        result = set()
        if question.state in self.get_viewable_states(user):
            result = self.get_viewable_fields_student(question)
            if user.is_organisation():
                result |= self.get_viewable_fields_organisation(question)
            if user.is_manager():
                user = user.as_manager()
                if user.is_central_manager():
                    result |= self.get_viewable_fields_central_manager(question)
                if user.is_regional_manager():
                    result |= self.get_viewable_fields_regional_manager(question)
        return result
    
    def get_editable_fields(self, user, question):
        result = set()
        if question.state in self.get_editable_states(user):
            result = self.get_editable_fields_student(question)
            if user.is_organisation():
                result |= self.get_editable_fields_organisation(question)
            if user.is_manager():
                user = user.as_manager()
                if user.is_central_manager():
                    result |= self.get_editable_fields_central_manager(question)
                if user.is_regional_manager():
                    result |= self.get_editable_fields_regional_manager(question)
        return result
    
    
    """
    VIEWABLE_FIELDS_STUDENT = {
        'question_text', 'reason', 'purpose', 'remarks', 'organisation'
    }

    VIEWABLE_FIELDS_STUDENT_2 = {
        DRAFT_QUESTION: {},
        NEW_QUESTION: {},
        INTAKE_QUESTION: {},
        IN_PROGRESS_QUESTION_CENTRAL: {},
        PROCESSED_QUESTION_CENTRAL: {},
        IN_PROGRESS_QUESTION_REGIONAL: {},
        PUBLIC_QUESTION: {'question_text', 'reason', 'purpose', 'remarks', 'organisation'},
        RESERVED_QUESTION: {'question_text', 'reason', 'purpose', 'remarks', 'organisation'},
        ONGOING_QUESTION: {},
        FINISHED_QUESTION: {'question_text', 'reason', 'purpose', 'remarks', 'organisation'},
        DENIED_QUESTION: {},
        REVOKED_QUESTION: {},
    }

    EDITABLE_FIELDS_STUDENT = {
        DRAFT_QUESTION: {},
        NEW_QUESTION: {},
        INTAKE_QUESTION: {},
        IN_PROGRESS_QUESTION_CENTRAL: {},
        PROCESSED_QUESTION_CENTRAL: {},
        IN_PROGRESS_QUESTION_REGIONAL: {},
        PUBLIC_QUESTION: {},
        RESERVED_QUESTION: {},
        ONGOING_QUESTION: {},
        FINISHED_QUESTION: {},
        DENIED_QUESTION: {},
        REVOKED_QUESTION: {},
    }

    VIEWABLE_FIELDS_ORGANISATION = {
        DRAFT_QUESTION: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'creation_date', 'state', 'keyword', 'question_subject'
        },
        NEW_QUESTION: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'creation_date', 'state', 'keyword', 'question_subject'
        },
        INTAKE_QUESTION: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'creation_date', 'state', 'keyword', 'question_subject'
        },
        IN_PROGRESS_QUESTION_CENTRAL: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'creation_date', 'state', 'keyword', 'question_subject'
        },
        PROCESSED_QUESTION_CENTRAL: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'creation_date', 'state', 'keyword', 'question_subject'
        },
        IN_PROGRESS_QUESTION_REGIONAL: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'creation_date', 'state', 'keyword', 'question_subject'
        },
        PUBLIC_QUESTION: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'creation_date', 'state', 'keyword', 'question_subject'
        },
        RESERVED_QUESTION: {},
        ONGOING_QUESTION: {},
        FINISHED_QUESTION: {},
        DENIED_QUESTION: {},
        REVOKED_QUESTION: {},
    }

    EDITABLE_FIELDS_ORGANISATION = {
        DRAFT_QUESTION: {
            'question_text', 'reason', 'purpose', 'own_contribution', 'remarks', 'deadline', 'keyword', 'question_subject'
        },
        NEW_QUESTION: {},
        INTAKE_QUESTION: {},
        IN_PROGRESS_QUESTION_CENTRAL: {},
        PROCESSED_QUESTION_CENTRAL: {},
        IN_PROGRESS_QUESTION_REGIONAL: {},
        PUBLIC_QUESTION: {},
        RESERVED_QUESTION: {},
        ONGOING_QUESTION: {},
        FINISHED_QUESTION: {},
        DENIED_QUESTION: {},
        REVOKED_QUESTION: {},
    }
    'draft', 'new', 'intake', 'in process central', 'processed central', 'in process regional', 'public', 'reserved', 'ongoing', 'finished', 'denied', 'revoked'

    'question_text'
    'reason'
    'purpose'
    'own_contribution'
    'remarks'
    'internal_remarks'
    'deadline'
    'public'
    'creation_date'
    'active'
    'state'
    'organisation'
    'student'
    'completion_date'
    'region'
    'keyword'
    'question_subject'
    'study_field'


    def get_viewable_states(self, user):
        result = {Question.PUBLIC_QUESTION, Question.RESERVED_QUESTION, Question.FINISHED_QUESTION}
        if user.is_organisation():
            result |= {state[0] for state in Question.STATE_SELECT}
        if user.is_manager():
            user = user.as_manager()
            if user.is_central_manager():
                result |= {Question.DRAFT_QUESTION, Question.NEW_QUESTION,
                           Question.IN_PROGRESS_QUESTION_CENTRAL, Question.PROCESSED_QUESTION_CENTRAL}
            if user.is_regional_manager():
                result |= {Question.INTAKE_QUESTION, Question.PROCESSED_QUESTION_CENTRAL,
                           Question.IN_PROGRESS_QUESTION_REGIONAL, Question.ONGOING_QUESTION}
        return result

    def get_editable_states(self, user):
        result = set()
        if user.is_organisation():
            result |= {Question.DRAFT_QUESTION}
        if user.is_manager():
            user = user.as_manager()
            if user.is_central_manager():
                result |= {Question.DRAFT_QUESTION, Question.NEW_QUESTION,
                           Question.IN_PROGRESS_QUESTION_CENTRAL, Question.PROCESSED_QUESTION_CENTRAL}
            if user.is_regional_manager():
                result |= {Question.INTAKE_QUESTION, Question.IN_PROGRESS_QUESTION_REGIONAL, Question.PUBLIC_QUESTION,
                           Question.RESERVED_QUESTION, Question.ONGOING_QUESTION}
        assert result & self.get_viewable_states(user) == result  # sanity check
        return result

    def get_viewable_fields_student(self, question):
        return self.VIEWABLE_FIELDS_STUDENT[question.state]

    def get_editable_fields_student(self, question):
        return self.EDITABLE_FIELDS_STUDENT[question.state]



    def get_viewable_fields(self, user, question):

        pass

    def get_editable_states(self, user, question):
        # for permission, state in user.get_all_permissions(), :
        result = set()
        if user.is_anonymous():
            pass
        if user.is_organisation():
            user = user.as_organisation()

        if user.is_manager():
            user = user.as_manager()
            if user.is_central_manager():
                pass
            if user.is_regional_manager():
                pass
    """
    """
    def get_next_states(self, state):
        next_states = {
            # Question.DRAFT_QUESTION: ([Question.NEW_QUESTION, Question.DENIED_QUESTION, Question.REVOKED_QUESTION]),
            DRAFT_QUESTION: ([NEW_QUESTION, DENIED_QUESTION, REVOKED_QUESTION]),
            NEW_QUESTION: ([INTAKE_QUESTION, DENIED_QUESTION, REVOKED_QUESTION]),
            INTAKE_QUESTION: ([IN_PROGRESS_QUESTION_CENTRAL, DENIED_QUESTION, REVOKED_QUESTION]),
            IN_PROGRESS_QUESTION_CENTRAL: ([PROCESSED_QUESTION_CENTRAL, DENIED_QUESTION, REVOKED_QUESTION]),
            PROCESSED_QUESTION_CENTRAL: ([IN_PROGRESS_QUESTION_REGIONAL, DENIED_QUESTION, REVOKED_QUESTION]),
            IN_PROGRESS_QUESTION_REGIONAL: ([PUBLIC_QUESTION, DENIED_QUESTION, REVOKED_QUESTION]),
            PUBLIC_QUESTION: ([RESERVED_QUESTION, DENIED_QUESTION, REVOKED_QUESTION]),
            RESERVED_QUESTION: ([ONGOING_QUESTION, DENIED_QUESTION, REVOKED_QUESTION]),
            ONGOING_QUESTION: ([FINISHED_QUESTION, DENIED_QUESTION, REVOKED_QUESTION]),
            FINISHED_QUESTION: ([DENIED_QUESTION, REVOKED_QUESTION]),
            DENIED_QUESTION: ([]),
            REVOKED_QUESTION: ([]),
        }
    """


class Permissions:
    pass
