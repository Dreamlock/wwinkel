from django.utils.translation import ugettext_lazy as _
from custom_users.models import User, OrganisationUser, ManagerUser

class StateIndex:
    state_names = (
        'draft', 'in_progress_central', 'processed_central', 'in_progress_regional'
    )

    DRAFT_QUESTION = 0
    IN_PROGRESS_QUESTION_CENTRAL = 1
    PROCESSED_QUESTION_CENTRAL = 2
    IN_PROGRESS_QUESTION_REGIONAL = 3
    PUBLIC_QUESTION = 4
    RESERVED_QUESTION = 5
    ONGOING_QUESTION = 6
    FINISHED_QUESTION = 7
    DENIED_QUESTION = 8
    REVOKED_QUESTION = 9

    STATE_SELECT = (
        (DRAFT_QUESTION, _('draft')),
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

    def get_viewable_states(self, user):

        pass

    def get_editable_states(self, user):
        # for permission, state in user.get_all_permissions(), :

        if user.is_organisation():
            user = user.as_organisation()
        if user.is_manager():
            pass

    def get_next_states(self, state):
        pass


class Permissions:
    pass
