"""
Admin configuration for the accounts app.
"""

# Django imports
from django.contrib import admin

# Local imports
from .models import User, Username, Referral, Referred

# Register your models here.
admin.site.register(User)
admin.site.register(Username)
admin.site.register(Referral)
admin.site.register(Referred)
