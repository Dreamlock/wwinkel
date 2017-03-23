from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique = True, )
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.email.strip()

    objects = BaseUserManager()


