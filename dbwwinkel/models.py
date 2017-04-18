from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import datetime
from django.utils.translation import ugettext_lazy as _

from custom_users.models import Region


class State(models.Model):
    # TODO: possible states choice (bv. new, active, closed,...)
    '''STATE_SELECT = (
        ('new', 'new'),
        ('active', 'active'),
        ('closed', 'closed'),
    )'''
    STATE_SELECT = (
        ('new', 'new'),
        ('intake', 'intake'),
        ('in_progress', 'in progress'),
        ('draft', 'draft'),
        ('free', 'free'),
        ('verwerkt', 'verwerkt'),
        ('denied', 'denied'),
        ('ingetrokken', 'ingetrokken'),
        ('in_option', 'in option'),
        ('running', 'running'),
        ('finished', 'finished'),
    )

    state = models.CharField(max_length=10)


def build_question_permissions():
    """
    Generate a list of permissions given the different states that a Question can be in.
    For example: a new Question is editable by the organisation that made the question, but an active Question is not.
    :return: a list of tuples containing all the permissions for the Question based on the STATE_SELECT member of State.
    """
    result = set()
    for element in State.STATE_SELECT:
        result.add(('view_'+element[0]+'_question', 'Can view '+element[1]+' question'))
        result.add(('change_'+element[0]+'_question', 'Can change '+element[1]+' question'))
    return result


class Question(models.Model):
    # Visible and editable: mandatory
    question_text = models.TextField()
    reason = models.TextField()
    purpose = models.TextField()
    own_contribution = models.TextField()

    # Visible and editable: optional
    remarks = models.TextField(blank=True)
    internal_remarks = models.TextField(blank=True)
    how_know_WW = models.TextField(blank=True)
    deadline = models.DateField(blank=True, null=True)

    public = models.BooleanField()

    # metadata: invisible
    creation_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    status = models.ForeignKey(State)

    region = models.ManyToManyField(Region)  # TODO: Check compatibility new field with forms (shouldn't be added by organisation)

    organisation = models.ForeignKey(settings.AUTH_USER_MODEL)

    def clean(self):
        if self.deadline is not None and self.deadline < datetime.date.today():
            raise ValidationError({'deadline': _('Deadlines kunnen niet in het verleden zijn')})

    def get_status_name(self):
        return self.status.state

    status_name = property(get_status_name)

    class Meta:
        permissions = build_question_permissions()

'''
class QuestionPermissionsBackend:

    def has_perm(self, user_obj, perm, obj=None):
        if not obj:
            return False
        #if user_obj.id is
'''