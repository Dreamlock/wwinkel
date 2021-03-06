from django.utils import translation
from custom_users.models import *
from dbwwinkel.models import Question
from django.contrib.auth.backends import ModelBackend


class QuestionPermissionsBackend(ModelBackend):
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
            question_state = str(question.state)

        checker = False

        if user_obj.is_manager():
            user_obj = ManagerUser.objects.get(id=user_obj.id)
            if (len(user_obj.region.filter(question__id=question.id)) > 0
                    or user_obj.region.filter(region=Region.CENTRAL_REGION)):
                checker = True

        elif user_obj.is_organisation():
                org_user = OrganisationUser.objects.get(id = user_obj.id)
                user_of_question = question.organisation

                if org_user.id == user_of_question.id:
                    checker = True

        if checker:
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
