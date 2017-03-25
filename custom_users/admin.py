from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User
from .forms import UserChangeForm, UserCreationForm


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
        (None, {'fields': ('email', 'password')}),
        (_('Important dates'), {'fields': ('date_joined', 'last_login')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'user_permissions')}),
    )
    readonly_fields = ('date_joined', 'last_login')

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


# Register UserAdmin.
admin.site.register(User, UserAdmin)
