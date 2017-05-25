from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import EmailField, URLField, TextField
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from django.conf import settings
from django.core.validators import RegexValidator


class Keyword(models.Model):
    """
    Representation of a keyword. Has a many to many relationship with Question (a question can have multiple keywords
    and a keyword can belong to multiple questions)
    """

    key_word = models.CharField(max_length=33, unique=True)

    def __str__(self):
        return self.key_word


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


class OrganisationManager(UserManager):
    def is_organisation(self):
        return True


class AbstractUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('This email is already used.')
        },
    )

    # first_name = models.CharField(_('first name'), max_length=50, blank=True)
    # last_name = models.CharField(_('last name'), max_length=50, blank=True)
    # telephone = models.PositiveIntegerField(_('telephone number'), blank=True)
    # gsm = models.PositiveIntegerField(_('gsm number'), blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )

    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_full_name(self):
        return self.email.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.email.strip()

        # def get_username(self):
        # return getattr(self, self.USERNAME_FIELD)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Province(models.Model):
    class Meta:
        verbose_name = _('province')
        verbose_name_plural = _('provinces')

    ANTWERP_REGION = 0
    EAST_FLANDERS_REGION = 1
    FLEMISH_BRABANT_REGION = 2
    LIMBURG_REGION = 3
    WEST_FLANDERS_REGION = 4
    BRUSSELS_REGION = 5
    PROVINCE_SELECT = (
        (ANTWERP_REGION, _('Antwerpen')),
        (EAST_FLANDERS_REGION, _('Oost-Vlaanderen')),
        (FLEMISH_BRABANT_REGION, _('Vlaams-Brabant')),
        (LIMBURG_REGION, _('Limburg')),
        (WEST_FLANDERS_REGION, _('West-Vlaanderen')),
        (BRUSSELS_REGION, _('Brussel')),
    )

    province = models.PositiveIntegerField(unique=True, choices=PROVINCE_SELECT)

    def __str__(self):
        return str(self.PROVINCE_SELECT[self.province][1])


class Address(models.Model):
    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    province = models.ForeignKey(Province)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    street_name = models.CharField(max_length=40)
    street_number = models.CharField(max_length=15)  # char om bv. 27B toe te staan.

    def __str__(self):
        return self.street_name + ' ' + str(self.street_number) + ', ' + self.city


class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=50, null=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True)
    telephone = models.CharField(_('telephone number'), max_length=20, null=True)
    gsm = models.CharField(_('gsm number'), max_length=20, null=True)

    def __str__(self):
        if self.first_name is None or self.last_name is None:
            return super().__str__()
        return self.last_name + ', ' + self.first_name

    def is_organisation(self):
        return OrganisationUser.objects.filter(id=self.id).exists()

    def as_organisation(self):
        if self.is_organisation():
            return OrganisationUser.objects.get(id=self.id)
        return None

    def is_manager(self):
        return ManagerUser.objects.filter(id=self.id).exists()

    def is_central_manager(self):
        if self.is_manager:
            m_user = ManagerUser.objects.get(id = self.id)
            if m_user.region.filter(region = Region.CENTRAL_REGION).exists():
                return True

        return False

    def is_regional_manager(self):
        if self.is_manager():
            m_user = ManagerUser.objects.get(id=self.id)
            if m_user.region.exclude(region=Region.CENTRAL_REGION).exists():
                return True
        return False

    def as_manager(self):
        if self.is_manager():
            return ManagerUser.objects.get(id=self.id)
        return None


class LegalEntity(models.Model):
    entity = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return '{0}'.format(self.entity)


class OrganisationType(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type


class KnowFrom(models.Model):
    knowfrom = models.TextField()

    def __str__(self):
        return self.knowfrom


class Organisation(models.Model):
    name = models.CharField('Naam', help_text='Naam van de organisatie.', max_length=255, unique=True)
    recognised_abbreviation = models.CharField(max_length=31, blank=True, null=True)

    legal_entity = models.ForeignKey(LegalEntity)
    address = models.ForeignKey(Address)

    telephone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20, blank=True, null=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    mail = models.EmailField()

    goal = models.TextField()
    remarks = models.TextField(blank=True, null=True)

    creation_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    keyword = models.ManyToManyField(Keyword)
    type = models.ForeignKey(OrganisationType)

    know_from = models.ForeignKey(KnowFrom, null=True, blank=True)

    def __str__(self):
        return self.name


class OrganisationUser(User):
    class Meta:
        verbose_name = _('organisation user')
        verbose_name_plural = _('organisation users')

    organisation = models.OneToOneField(Organisation)  # , related_name='user_organisation') TODO: OnetoOnekey


@receiver(post_save, sender=OrganisationUser)
def organisation_user_created(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        user.groups.set([Group.objects.get(name='Organisations')])
        print('send mail: org added')
        """
        send_mail(
            'Organisatie toegevoegd',
            'Hey, er is een nieuwe org toegevoegd',
            'wwinkel.noreply@gmail.com',
            ['EMAIL', 'MANAGERS'],
            fail_silently=True,
        )
        """


class Region(models.Model):
    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')

    ANTWERP_REGION = 0
    EAST_FLANDERS_REGION = 1
    FLEMISH_BRABANT_REGION = 2
    LIMBURG_REGION = 3
    WEST_FLANDERS_REGION = 4
    CENTRAL_REGION = 5
    BRUSSELS_REGION=6
    REGION_SELECT = (
        (ANTWERP_REGION, _('Antwerpen')),
        (EAST_FLANDERS_REGION, _('Oost-Vlaanderen')),
        (FLEMISH_BRABANT_REGION, _('Vlaams-Brabant')),
        (LIMBURG_REGION, _('Limburg')),
        (WEST_FLANDERS_REGION, _('West-Vlaanderen')),
        (CENTRAL_REGION, _('Centraal')),
        (BRUSSELS_REGION, _('Brussel'))
    )
    region = models.PositiveIntegerField(unique=True, choices=REGION_SELECT)

    def __str__(self):
        return str(self.REGION_SELECT[self.region][1])


class ManagerUser(User):
    class Meta:
        verbose_name = _('management user')
        verbose_name_plural = _('management users')

    region = models.ManyToManyField(Region)

    def is_central_manager(self):
        return self.region.filter(region=Region.CENTRAL_REGION).exists()

    def is_regional_manager(self):
        return self.region.exclude(region=Region.CENTRAL_REGION).exists()


@receiver(post_save, sender=ManagerUser)
def manager_user_created(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        if user.is_central_manager():
            user.groups.set([Group.objects.get(name='Central Managers')])
        if user.is_regional_manager():
            user.groups.set([Group.objects.get(name='Regional Managers')])

class QuestionInstitution(models.Model):
    address = models.ForeignKey(Address)
    name = models.TextField()

class Mediator(User):
    jobfunction = models.TextField()
    quesiotninstitution = models.ManyToManyField(QuestionInstitution)

class OrganisationContact(models.Model):
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=20)
    cell = models.CharField(max_length=20)
    address = models.ForeignKey(Address, null=True)
    job_function = models.TextField()
    email = models.EmailField(
        _('email address'),
        error_messages={
            'unique': _('This email is already used.')
        },
    )
    remarks = models.TextField()
    organisation = models.ForeignKey(Organisation)