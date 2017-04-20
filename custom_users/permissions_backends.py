from .models import *
from dbwwinkel.models import Question, State

#def question_authentication(user):


class QuestionPermissionsBackend:
    def has_perm(self, user_obj, perm, question=None):
        if not question:
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
    print("")
