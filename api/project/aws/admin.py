from django.contrib import admin
from aws.models import SESEmailTemplate, TemplatedEmail
# Register your models here.

admin.site.register(SESEmailTemplate)
admin.site.register(TemplatedEmail)
