from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CustomUsersConfig(AppConfig):
    name = 'custom_users'
    verbose_name = _('users')
