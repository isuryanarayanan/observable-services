from django.db import models
import boto3
import os
from django.conf import settings
import json


# Create your models here.

TEMPLATES = (
    ('WelcomeTemplate', 'WelcomeTemplate'),

    ('EmailVerificationTemplate', 'EmailVerificationTemplate'),
    ('EmailVerificationSuccessTemplate', 'EmailVerificationSuccessTemplate'),

    ('ForgotPasswordTemplate', 'ForgotPasswordTemplate'),
    ('ForgotPasswordSuccessTemplate', 'ForgotPasswordSuccessTemplate'),

    ('ValidationTemplate', 'ValidationTemplate'),
    ('ValidationSuccessTemplate', 'ValidationSuccessTemplate'),

    ('ResetPasswordTemplate', 'ResetPasswordTemplate'),
    ('ResetPasswordSuccessTemplate', 'ResetPasswordSuccessTemplate'),
)


class SESEmailTemplate(models.Model):
    template_identifier = models.CharField(
        max_length=250, choices=TEMPLATES, unique=True)
    template_subject = models.TextField()
    template_text_part = models.FileField(upload_to='aws/ses/templates/txt/')
    template_html_part = models.FileField(upload_to='aws/ses/templates/html/')
    template_keys = models.JSONField(default=dict)

    def __str__(self):
        return self.template_identifier


EMAIL_STATUS = (
    ('PENDING', 'PENDING'),
    ('SENT', 'SENT'),
    ('FAILED', 'FAILED'),
)


class TemplatedEmail(models.Model):
    email = models.EmailField()
    template = models.ForeignKey(SESEmailTemplate, on_delete=models.CASCADE)
    template_data = models.JSONField(default=dict)

    status = models.CharField(
        max_length=250,
        choices=EMAIL_STATUS,
        default='PENDING'
    )

    def __str__(self):
        return self.email

    def get_template_identifier(self):
        mode = os.environ.get('GENIE_CONFIGURATION_KEY', None)
        return str(mode).upper()+"-"+self.template.template_identifier

    def save(self, *args, **kwargs):

        # Check if the template data is correlated with the template keys
        template_keys = self.template.template_keys
        template_data = self.template_data

        for key in template_keys:
            if key not in template_data:
                raise Exception(
                    "The template data is not correlated with the template keys")

        super(TemplatedEmail, self).save(*args, **kwargs)

    def send(self):
        try:
            ses = boto3.client('ses', region_name='ap-south-1')

            # Define the email parameters
            source = settings.DEFAULT_NOTIFICATION_EMAIL
            to_addresses = [self.email]

            response = ses.send_templated_email(
                Source=source,
                Destination={
                    'ToAddresses': to_addresses
                },
                # Template names are appended with the mode of deployment
                # to avoid conflicts in production and development
                # because all deployments use the same AWS account
                Template=self.get_template_identifier(),
                TemplateData=json.dumps(self.template_data)
            )
            print(response)

            # Get otp object with id and update the status to delivered
            self.status = 'SENT'
            self.save()
        except Exception as e:
            self.status = 'FAILED'
            self.save()
            raise e
