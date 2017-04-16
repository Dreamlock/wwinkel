from .models import *
from dbwwinkel.models import Question

#def question_authentication(user):

class QuestionPermissionsBackend:
    def has_perm(self, user_obj, perm, question=None):
        if not question:
            return False

        permissions = user_obj.get_all_permissions(question)
        print(permissions)

        #if question.status == :

        if perm == '':
            pass
            #if user_obj.id is