from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import EmailField, URLField, TextField
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.validators import RegexValidator


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
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
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

    PROVINCE_SELECT = (
        ('ANT', _('Antwerp')),
        ('OVL', _('East Flanders')),
        ('WVL', _('West Flanders')),
        ('OVL', _('East Flanders')),
        ('VBR', _('Flemish Brabant'))
    )

    province = models.CharField(max_length=3, unique=True, choices=PROVINCE_SELECT)
    """
    def __str__(self):
        return self.province
    """


class Address(models.Model):
    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    province = models.ForeignKey(Province)
    city = models.CharField(max_length=255)
    postal_code = models.PositiveIntegerField()
    street_name = models.CharField(max_length=40)
    street_number = models.CharField(max_length=15)  # char om bv. 27B toe te staan.

    def __str__(self):
        return self.street_name + ' ' + str(self.street_number) + ', ' + self.city


class User(AbstractUser):
    first_name = models.CharField(_('first name'), max_length=50, null=True)
    last_name = models.CharField(_('last name'), max_length=50, null=True)
    telephone = models.PositiveIntegerField(_('telephone number'), null=True)
    gsm = models.PositiveIntegerField(_('gsm number'), null=True)

    def __str__(self):
        if self.first_name is None or self.last_name is None:
            return super().__str__()
        return self.last_name + ', ' + self.first_name

    '''
    def is_organisation(self):
        try:
            OrganisationUser.objects.get(pk=self.id)
        except ObjectDoesNotExist:
            return False
        return True

    def is_manager(self):
        try:
            ManagerUser.objects.get(pk=self.id)
        except ObjectDoesNotExist:
            return False
        return True
    '''


class LegalEntity(models.Model):
    entity = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return '{0}'.format(self.entity)


class OrganisationType(models.Model):
    type = models.CharField(max_length=100)


class Organisation(models.Model):
    name = models.CharField(max_length=255, unique=True)
    recognised_abbreviation = models.CharField(max_length=31, blank=True)

    legal_entity = models.ForeignKey(LegalEntity)
    address = models.ForeignKey(Address)

    telephone = models.IntegerField()
    fax = models.IntegerField(blank=True, null=True)
    website = URLField(max_length=255, null=True, blank=True)

    goal = models.TextField()
    remarks = models.TextField(blank=True, null=True)

    creation_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class OrganisationUser(User):
    class Meta:
        verbose_name = _('organisation user')
        verbose_name_plural = _('organisation users')

    organisation = models.ForeignKey(Organisation)  # , related_name='user_organisation')


class Region(models.Model):
    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')

    PROVINCE_SELECT = (
        ('ANT', _('Antwerp')),
        ('OVL', _('East Flanders')),
        ('WVL', _('West Flanders')),
        ('CEN', _('Central')),
    )
    region = models.CharField(max_length=3, unique=True, choices=PROVINCE_SELECT)

    def __str__(self):
        return self.region


class ManagerUser(User):
    class Meta:
        verbose_name = _('management user')
        verbose_name_plural = _('management users')

    region = models.ManyToManyField(Region)


