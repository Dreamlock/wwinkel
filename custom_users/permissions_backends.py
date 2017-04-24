from django.utils import translation
from custom_users.models import *
from dbwwinkel.models import Question, State


class QuestionPermissionsBackend:
    def has_perm(self, user_obj, perm, question=None):
        # perm = 'edit_question', 'view_question'
        if not question:
            return False
        if not isinstance(question, Question):
            return False
        permissions = user_obj.get_all_permissions()
        # print(str(user_obj))
        # print(permissions)

        question_state = ''
        with translation.override('en'):
            question_state = str(question.status)

        if ((user_obj.is_manager()
                and (len(user_obj.region.filter(question__id=question.id)) > 0)
                    or user_obj.region.filter(region=Region.CENTRAL_REGION))
                or (user_obj.is_organisation()
                    and user_obj.organisation.filter(question__id=question.id))):
            if perm == 'view_question':
                for permission in permissions:
                    # check of dat str(question.status) in permission zit (als ok: has_perm=true)
                    if 'view_' + question_state.replace(' ', '_') in permission:
                        return True
            if perm == 'edit_question':
                for permission in permissions:
                    if 'edit_' + question_state.replace(' ', '_') in permission:
                        return True
        return False
