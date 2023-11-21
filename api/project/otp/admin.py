"""
Admin configuration for the otp app.
"""
# Django imports
from django.contrib import admin

# App imports
from otp.models import OneTimePassword


@admin.register(OneTimePassword)
class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'code', 'created_at',
                    'expires_at', 'expiry_time')
    search_fields = ('user__email', 'code', 'status')
