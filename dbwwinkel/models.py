import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from custom_users.models import Region, Organisation, Address, User, Keyword


class Education(models.Model):
    """Represents a field of study (like biology or computer science)"""

    education = models.CharField(max_length=33, unique=True)

    def __str__(self):
        return self.education


class Institution(models.Model):
    name = models.CharField(max_length=40)
    address = models.ForeignKey(Address)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.TextField()
    institution = models.ManyToManyField(Institution, through='FacultyOf')


class FacultyOf(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    education = models.ManyToManyField(Education)


class Student(models.Model):
    first_name = models.CharField(max_length=33)
    last_name = models.CharField(max_length=45)

    mobile = models.CharField(max_length=20)
    email = models.EmailField()

    status = models.BooleanField(default=True)  # Waarvoor dient dit?

    education = models.ForeignKey(Education)
    address = models.ForeignKey(Address)


class Person(models.Model):
    class Meta:
        abstract = True

    first_name = models.CharField(max_length=33)
    last_name = models.CharField(max_length=33)

    email = models.EmailField()
    tel = models.CharField(max_length=18)

    address = models.ForeignKey(Address)


class Promotor(Person):
    expertise = models.TextField()
    institution = models.ForeignKey(Institution)
    promo_class = models.CharField(max_length=100, null=True)


class InstitutionContact(Person):
    institution = models.ForeignKey(Institution)


class Intake(models.Model):
    date = models.DateTimeField(default=timezone.now)
    remarks = models.TextField()


class Attachment(models.Model):
    name = models.TextField()
    type = models.TextField()  # docx, csv, txt, ...


class LogRecord(models.Model):
    subject = models.TextField()
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    creator = models.ManyToManyField(User)


class Log(models.Model):
    record = models.ManyToManyField(LogRecord)


class QuestionType(models.Model):
    type = models.TextField()


class QuestionSubject(models.Model):
    """
    Represents what subject(s) the question belongs to. This is primarly used to search for a specific question.
    with facet search.
    """

    subject = models.CharField(max_length=33, unique=True)

    def __str__(self):
        return self.subject


class Question(models.Model):
    DRAFT_QUESTION = 0
    NEW_QUESTION = 1
    INTAKE_QUESTION = 2
    IN_PROGRESS_QUESTION_CENTRAL = 3
    PROCESSED_QUESTION_CENTRAL = 4
    IN_PROGRESS_QUESTION_REGIONAL = 5
    PUBLIC_QUESTION = 6
    RESERVED_QUESTION = 7
    ONGOING_QUESTION = 8
    FINISHED_QUESTION = 9
    DENIED_QUESTION = 10
    REVOKED_QUESTION = 11

    STATE_SELECT = (
        (DRAFT_QUESTION, _('draft')),
        (NEW_QUESTION, _('new')),
        (INTAKE_QUESTION, _('intake')),
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

    # Visible and editable: mandatory
    question_text = models.TextField()
    reason = models.TextField()
    purpose = models.TextField()
    own_contribution = models.TextField()

    # Visible and editable: optional
    remarks = models.TextField(blank=True)
    internal_remarks = models.TextField(blank=True)
    deadline = models.DateField(blank=True, null=True)
    public = models.BooleanField()

    #The corresponding organisation
    organisation = models.ForeignKey(Organisation)

    # metadata: invisible
    creation_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    state = models.IntegerField(choices=STATE_SELECT, default=DRAFT_QUESTION)
    region = models.ManyToManyField(Region)

    # Faceting data
    institution = models.ManyToManyField(Institution)
    promotor = models.ManyToManyField(Promotor)
    faculty = models.ManyToManyField(Faculty)
    education = models.ManyToManyField(Education)
    keyword = models.ManyToManyField(Keyword)
    question_subject = models.ManyToManyField(QuestionSubject, blank=True)
    type = models.ForeignKey(QuestionType, null=True)

    student = models.ForeignKey(Student, null=True)
    completion_date = models.DateTimeField(null=True)  # When the question was round up

    history = HistoricalRecords()

    def __str__(self):
        return self.question_text

    def clean(self):
        if self.deadline is not None and self.deadline < datetime.date.today():
            raise ValidationError({'deadline': _('Deadlines kunnen niet in het verleden zijn')})

    class Meta:
        default_permissions = ('add', 'delete')
        permissions = (
            # ('add_question', _('Can add question')),
            # ('delete_question', _('Can delete question')),
            # ('view_question', _('Can view question (don\'t assign to user)')),
            # ('edit_question', _('Can edit question (don\'t assign to user)')),

            ('view_draft_question', _('Can view draft question')),
            ('edit_draft_question', _('Can edit draft question')),
            ('view_in_progress_central_question', _('Can view in progress question central')),
            ('edit_in_progress_central_question', _('Can edit in progress question central')),
            ('view_processed_central_question', _('Can view processed question central')),
            ('edit_processed_central_question', _('Can edit processed question central')),
            ('view_in_progress_regional_question', _('Can view in progress question regional')),
            ('edit_in_progress_regional_question', _('Can edit in progress question regional')),
            # ('view_public_question', _('Can view public question')),
            ('edit_public_question', _('Can edit public question')),
            # ('view_reserved_question', _('Can view reserved question')),
            ('edit_reserved_question', _('Can edit reserved question')),
            ('view_ongoing_question', _('Can view ongoing question')),
            ('edit_ongoing_question', _('Can edit ongoing question')),
            # ('view_finished_question', _('Can view finished question')),
            ('edit_finished_question', _('Can edit finished question')),
            ('view_denied_question', _('Can view denied question')),
            ('edit_denied_question', _('Can edit denied question')),
            ('view_revoked_question', _('Can view revoked question')),
            ('edit_revoked_question', _('Can edit revoked question')),  # TODO: add permissions for new/intake question
        )
        # permissions = build_question_permissions()


@receiver(post_save, sender=Question)
def question_changed_status(sender, **kwargs):
    question = kwargs['instance']
    if kwargs['created']:
        print('send mail: question added')
        # print(kwargs['update_fields'])
