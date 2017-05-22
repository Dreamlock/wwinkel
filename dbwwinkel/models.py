import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from simple_history.models import HistoricalRecords

from custom_users.models import Region, Organisation, Address, User, Keyword


class Education(models.Model):
    """Represents a field of study (like biology or computer science)"""

    education = models.CharField(verbose_name='opleiding', max_length=33, unique=True)

    def __str__(self):
        return self.education


class Institution(models.Model):
    name = models.CharField(verbose_name='naam', help_text='naam van de instelling', max_length=40, unique=True)
    address = models.ForeignKey(Address, verbose_name='adres', help_text='adres van de instelling')

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(verbose_name='naam', help_text='naam van de faculteit', max_length=40, unique=True)
    institution = models.ManyToManyField(Institution, through='FacultyOf')

    def __str__(self):
        return self.name


class FacultyOf(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    education = models.ManyToManyField(Education)


class Student(models.Model):
    first_name = models.CharField('voornaam', max_length=33)
    last_name = models.CharField('familienaam', max_length=45)

    mobile = models.CharField('gsm', max_length=20)
    email = models.EmailField(verbose_name='email')

    status = models.BooleanField(default=True)  # Waarvoor dient dit?

    education = models.ForeignKey(Education, help_text='opleiding van de student')
    address = models.ForeignKey(Address, help_text='adres van de student')


class Person(models.Model):
    class Meta:
        abstract = True

    first_name = models.CharField(max_length=33)
    last_name = models.CharField(max_length=33)

    email = models.EmailField()
    tel = models.CharField(max_length=18)

    address = models.ForeignKey(Address)

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Promotor(Person):
    expertise = models.TextField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
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
    education = models.ManyToManyField(Education)

    def __str__(self):
        return self.subject


class QuestionGroups(models.Model):
    pass


class Question(models.Model):
    NEW_QUESTION = 0
    INTAKE_QUESTION = 1
    IN_PROGRESS_QUESTION_CENTRAL = 2
    IN_PROGRESS_QUESTION_REGIONAL = 3
    PUBLIC_QUESTION = 4
    RESERVED_QUESTION = 5
    ONGOING_QUESTION = 6
    FINISHED_QUESTION = 7
    DENIED_QUESTION = 8
    REVOKED_QUESTION = 9

    STATE_SELECT = (
        (NEW_QUESTION, _('nieuw')),
        (INTAKE_QUESTION, _('intake')),
        (IN_PROGRESS_QUESTION_CENTRAL, _('in verwerking centraal')),
        (IN_PROGRESS_QUESTION_REGIONAL, _('in verwerking regionaal')),
        (PUBLIC_QUESTION, _('vrij')),
        (RESERVED_QUESTION, _('in optie')),
        (ONGOING_QUESTION, _('lopend')),
        (FINISHED_QUESTION, _('afgerond')),
        (DENIED_QUESTION, _('geweigerd')),
        (REVOKED_QUESTION, _('teruggetroken')),
    )

    # Visible and editable: mandatory
    question_text = models.TextField('vraag', help_text='wat is uw vraag?')
    reason = models.TextField('reden voor de vraag', help_text='hoe is uw vraag ontstaan?')
    purpose = models.TextField('doel van de vraag', help_text='hoe wilt u de resultaten van uw vraag gebruiken?')
    own_contribution = models.TextField('eigen bijdrage', help_text='kan u een bijdrage leveren aan de kosten?')

    # Visible and editable: optional
    remarks = models.TextField('opmerkingen', blank=True, default='')
    internal_remarks = models.TextField('interne opmerkingen', blank=True, default='')
    deadline = models.DateField(
        verbose_name='deadline vraag',
        help_text='Moet u binnen een bepaalde termijn antwoord op uw vraag hebben?',
        null=True,
        blank=True
    )
    public = models.BooleanField('vragen zijn publiek', blank=True, default=False)
    intake = models.ForeignKey(Intake, null=True, blank=True)
    attachment = models.ManyToManyField(Attachment, blank=True)

    # The corresponding organisation
    organisation = models.ForeignKey(Organisation, verbose_name='organisatie')

    # metadata: invisible
    creation_date = models.DateTimeField(default=timezone.now, editable=False, null=True, blank=True)
    active = models.BooleanField(default=True)
    state = models.IntegerField(choices=STATE_SELECT, default=NEW_QUESTION)

    region_processing =  region = models.ManyToManyField(
        Region, verbose_name='regio', related_name='question_region_process')

    region = models.ManyToManyField(
        Region, verbose_name='regio', help_text='huidige regio(s) die momenteel met de vraag bezig zijn'
    )




    # Faceting data
    institution = models.ManyToManyField(Institution, verbose_name='instelling')
    promotor = models.ManyToManyField(Promotor, verbose_name='promotor')
    faculty = models.ManyToManyField(Faculty, verbose_name='faculteit')
    education = models.ManyToManyField(Education, verbose_name='opleiding')
    keyword = models.ManyToManyField(Keyword, verbose_name='trefwoorden')
    question_subject = models.ManyToManyField(QuestionSubject, blank=True)
    type = models.ForeignKey(QuestionType, null=True)

    student = models.ForeignKey(Student, verbose_name='student', null=True)
    completion_date = models.DateTimeField(null=True)  # When the question was round up

    history = HistoricalRecords()
    question_group = models.ForeignKey(QuestionGroups)

    # methods on objects
    # build ins overwritten
    def __str__(self):
        return self.question_text

    def get_absolute_url(self):
        return reverse('detail', question_id=self.id)

    # own
    @property
    def possible_promotors(self):

        institutions = self.institution.all()

        promotor_list = Promotor.objects.none()
        for institution in institutions:
            promotor_list = promotor_list | institution.promotor_set.all()

        return promotor_list

    @property
    def organisation_name(self):
        return self.organisation.name

    @property
    def possible_faculty(self):

        institutions = self.institution.all()

        faculty_list = Promotor.objects.none()
        for institution in institutions:
            faculty_list = faculty_list | institution.faculty_set.all()

        return faculty_list

    @property
    def possible_education(self):

        p_education = Education.objects.none()
        for inst in self.institution.all():
            for fac in self.faculty.all():
                if FacultyOf.objects.filter(institution=inst, faculty=fac).exists():
                    fac_of = FacultyOf.objects.get(institution=inst, faculty=fac)
                    p_education = p_education | fac_of.education.all()

        return p_education

    @property
    def possible_subject(self):

        subject = QuestionSubject.objects.none()
        for edu in self.education.all():
            subject = subject | edu.questionsubject_set.all()

        return subject

    def remove_education(self, education):
        subject_education = education.questionsubject_set.all()

        intersect = subject_education & self.question_subject.all()

        for subject in intersect:
            to_remove = True
            for edu in self.education.all():
                if edu != education:
                    if subject in edu.questionsubject_set.all():
                        to_remove = False

            if to_remove:
                self.remove_faculty(subject)
        self.save()

    def remove_faculty(self, faculty):

        f_of_lst = []
        for inst in self.institution.all():
            if FacultyOf.objects.filter(institution=inst, faculty=faculty).exists():
                f_of = FacultyOf.objects.get(institution=inst, faculty=faculty)
                f_of_lst.append(f_of)

        for eu in self.education.all():
            to_remove = True
            for f_of in f_of_lst:
                if eu in f_of.education.all():
                    if f_of.faculty != faculty:
                        to_remove = False

            if to_remove:
                self.remove_education(eu)

        self.faculty.remove(faculty)
        self.save()

    def remove_institution(self, institution):

        proms_institution = institution.promotor_set.all()
        proms_question = self.promotor.all()

        intersect = proms_institution & proms_question

        for prom in intersect:
            self.promotor.remove(prom)

        self.institution.remove(institution)
        institution.question_set.remove(self)
        institution.save()
        self.save()

        faculty_institution = institution.faculty_set.all()
        faculty_question = self.faculty.all()

        intersect = faculty_institution & faculty_question

        for fac in intersect:
            to_remove = True
            for inst in self.institution.all():
                if inst != institution:
                    if fac in inst.faculty_set.all():
                        to_remove = False

            if to_remove:
                self.remove_faculty(fac)
        self.save()

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
            ('view_new_question', _('Can view new question')),
            ('edit_new_question', _('Can edit new question')),
            ('view_intake_question', _('Can view intake question')),
            ('edit_intake_question', _('Can edit intake question')),
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
            ('edit_revoked_question', _('Can edit revoked question')),
        )
        # permissions = build_question_permissions()


@receiver(post_save, sender=Question)
def question_changed_status(sender, **kwargs):
    question = kwargs['instance']
    if kwargs['created']:
        pass
        # print('send mail: question added')
        # print(kwargs['update_fields'])
