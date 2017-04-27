from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import *
from .forms import *
from dbwwinkel.models import *


class AddressInline(admin.StackedInline):
    model = Address


class OrganisationAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_date',)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_superuser', 'is_staff', 'date_joined')
    list_filters = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', ('first_name', 'last_name'))}),
        (_('Contact'), {'fields': ('telephone', 'gsm')}),
        (_('Important dates'), {'fields': ('date_joined', 'last_login')}),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions')
        }),
    )
    readonly_fields = ('date_joined', 'last_login')

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
        ('Extra', {
            'fields': ('telephone', 'gsm')
        })
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    # inlines = (AddressInline,)


class OrganisationUserAdmin(UserAdmin):
    form = OrganisationUserChangeForm
    add_form = OrganisationUserCreationForm

    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('organisation__name',)
    search_fields = ['organisation__name', 'first_name', 'last_name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Contact'), {'fields': ('telephone', 'gsm', 'organisation')}),
        (_('Important dates'), {'fields': ('date_joined', 'last_login')}),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions')
        }),
    )
    readonly_fields = ('date_joined', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
        ('Extra', {
            'fields': ('telephone', 'gsm', 'organisation')
        })
    )


class ManagerUserAdmin(UserAdmin):
    form = ManagerUserChangeForm
    add_form = ManagerUserCreationForm

    list_display = ('email',)
    list_filter = ('region',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('region'), {'fields': ('region',)}),
        (_('Important dates'), {'fields': ('date_joined', 'last_login')}),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions')
        }),
    )
    readonly_fields = ('date_joined', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
        ('Extra', {
            'fields': ('region',)
        })
    )
    filter_horizontal = ('groups', 'user_permissions', 'region')


# Register UserAdmin.
admin.site.register(LegalEntity)
admin.site.register(Address)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Province)
admin.site.register(User, UserAdmin)
admin.site.register(OrganisationUser, OrganisationUserAdmin)
admin.site.register(Region)
admin.site.register(ManagerUser, ManagerUserAdmin)
admin.site.register(StudyField)
