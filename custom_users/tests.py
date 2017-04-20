from django.test import TestCase
from custom_users.models import *
from custom_users.permissions_backends import *
from dbwwinkel.models import *

class QuestionPermissionBackendTestCase(TestCase):
    def setUp(self):

        Question.objects.create(
            question_text='Is This Question 1?',
            reason='Reason 1',
            purpose='Purpose 1',
            own_contribution='Budget contribution 1',
            remarks='Remark 1',
            internal_remarks='Internal remark 1',

        )
