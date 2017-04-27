import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wwinkel.settings")
django.setup()
from django.contrib.auth.models import Group, Permission
# from custom_users.models import *
# from dbwwinkel.models import *


organisation_perms = (
    'add_question',
    'view_draft_question',
    'edit_draft_question',
    'view_in_progress_central_question',
    'view_processed_central_question',
    'view_in_progress_regional_question',
    'view_ongoing_question',
    'view_denied_question',
    'view_revoked_question',
)

central_manager_perms = (
    'view_draft_question',
    'edit_draft_question',
    'view_in_progress_central_question',
    'edit_in_progress_central_question',
    'view_processed_central_question',
    'edit_processed_central_question',
)

regional_manager_perms = (
    'view_processed_central_question',
    'view_in_progress_regional_question',
    'edit_in_progress_regional_question',
    'edit_public_question',
    'edit_reserved_question',
    'view_ongoing_question',
    'edit_ongoing_question',
)

organisation_group, _ = Group.objects.get_or_create(name='Organisations')
organisation_group.permissions = [Permission.objects.get(codename=x) for x in organisation_perms]
organisation_group.save()

central_managers_group, _ = Group.objects.get_or_create(name='Central Managers')
central_managers_group.permissions = [Permission.objects.get(codename=x) for x in central_manager_perms]
central_managers_group.save()

regional_manager_group, _ = Group.objects.get_or_create(name='Regional Managers')
regional_manager_group.permissions = [Permission.objects.get(codename=x) for x in regional_manager_perms]
regional_manager_group.save()
