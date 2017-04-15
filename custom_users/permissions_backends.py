from .models import *


def OrganisationIsSelf():
    pass



class QuestionPermissionsBackend:
    def has_perm(self, user_obj, perm, obj=None):
        if not obj:
            return False

        if perm == '':
            pass
            #if user_obj.id is