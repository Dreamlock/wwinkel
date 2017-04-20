from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import datetime
from django.utils.translation import ugettext_lazy as _

from custom_users.models import Region, Organisation


class State(models.Model):
    # TODO: possible states choice (bv. new, active, closed,...)
    '''STATE_SELECT = (
        ('new', 'new'),
        ('active', 'active'),
        ('closed', 'closed'),
    )'''
    STATE_SELECT = (
        ('draft', _('draft')),
        ('ipcnt', _('in progress central')),
        ('procc', _('processed central')),
        ('ipreg', _('in progress regional')),
        ('free', _('free')),
        ('inopt', _('in option')),
        ('runng', _('running')),
        ('done', _('done')),
        ('denie', _('denied')),
        ('revok', _('revoked')),
    )

    state = models.CharField(max_length=10)

    def __str__(self):
        return self.state


def build_question_permissions():
    """
    Generate a list of permissions given the different states that a Question can be in.
    For example: a new Question is editable by the organisation that made the question, but an active Question is not.
    :return: a list of tuples containing all the permissions for the Question based on the STATE_SELECT member of State.
    """
    result = set()
    for element in State.STATE_SELECT:
        result.add(('view_'+element[0]+'_question', str(_('Can view '))+str(element[1])+str(_(' question'))))
        result.add(('change_'+element[0]+'_question', str(_('Can change '))+str(element[1])+str(_(' question'))))
    return result


class Keyword(models.Model):
    """
    Representation of a keyword. Has a many to many relationship with Question (a question can have multiple keywords
    and a keyword can belong to multiple questions)
    """

    key_word = models.CharField(max_length=33, unique=True)

class QuestionSubject(models.Model):
    """
    Represents what subject(s) the question belongs to. This is primarly used to search for a specific question.
    with facet search.
    """

    subject = models.CharField(max_length=33, unique=True)

    def __str__(self):
        return self.subject


class StudyField(models.Model):
    """Represents a field of study (like biology or computer science)"""

    study_field = models.CharField(max_length=33, unique=True)


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

    organisation = models.ForeignKey(Organisation)

    keyword = models.ManyToManyField(Keyword)
    question_subject = models.ManyToManyField(QuestionSubject)
    study_field = models.ManyToManyField(StudyField)

    def __str__(self):
        return self.question_text

    def clean(self):
        if self.deadline is not None and self.deadline < datetime.date.today():
            raise ValidationError({'deadline': _('Deadlines kunnen niet in het verleden zijn')})

    def get_status_name(self):
        state_names = [_("nieuw"), _("verwerking centraal"), _("verwerkt centraal"), _("verwerking_regionaal"),
                       _("vrij"), _("gereserveerd"),_("lopend"), _("afgerond"), _("geweigerd"), _("ingetrokken")]
        return state_names[self.status.id - 1]

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