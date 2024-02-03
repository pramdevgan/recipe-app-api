"""
Django Admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    search_fields = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', )}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1',
                'password2', 'name',
                'is_active', 'is_staff',
                'is_superuser'
            ),
        }),
    )


class RecipeAdmin(admin.ModelAdmin):

    list_display = ('title', 'time_minutes', 'price', 'link', 'display_tags')
    list_filter = ('title', 'tags')
    search_fields = ['title', 'tags']
    list_display_links = ('title', )

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'Tags'


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user')
    search_fields = ['name']
    list_filter = ('name', )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Tag, TagAdmin)
