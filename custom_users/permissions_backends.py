from custom_users.models import *
from dbwwinkel.models import Question, State

#def question_authentication(user):


class QuestionPermissionsBackend:
    def has_perm(self, user_obj, perm, question=None):
        # perm = 'edit_question', 'view_question'
        if not question:
            return False
        if not isinstance(question, Question):
            return False
        permissions = user_obj.get_all_permissions(question)
        print(permissions)
        return False

        """
        if perm in permissions and perm == 'view_new_question' and question.status == 'new':
            return True
        if perm in permissions and perm == 'edit_new_question' and question.status == 'new':
            return True
        """

        if perm == 'view_question':
            if ((user_obj.is_manager() and user_obj.region.region == question.region.region)
                    or (user_obj.is_organisation() and user_obj.organisation.id == question.organisation.id)):
                if user_obj.has_perm(''):
                    pass
                # for permission in permissions:
                    # if question.status.state
                pass

        if perm == 'edit_question':
            if user_obj.is_manager():
                if user_obj.region.region == Region.CENTRAL_REGION:
                    if (question.status.state == State.DRAFT_QUESTION
                            or question.status.state == State.IN_PROGRESS_QUESTION_CENTRAL
                            or question.status.state == State.PROCESSED_QUESTION_CENTRAL):
                        return True
                else:
                    if (question.region.region == user_obj.region.region):
                        if (question.status.state == State.IN_PROGRESS_QUESTION_REGIONAL
                                or question.status.state == State.PUBLIC_QUESTION
                                or question.status.state == State.RESERVED_QUESTION):
                            pass

                    pass
            pass
        elif perm == 'view_question':

            pass


        result = False
        if perm in permissions:
            for state in State.STATE_SELECT:
                if question.status == state[0]:
                    if state[0] in perm:
                        try:
                            user_obj.region.id == question.region.id
                        except ValueError:
                            pass

                        result = True
                    break
        return result

if __name__ == '__main__':
    admin = ManagerUser.objects.get(pk=1)
    print(str(admin))
    central_manager = ManagerUser.objects.get(pk=2)
