""" Signals fire when otp model is created. """

# Django import
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import boto3


from .models import OneTimePassword
from aws.models import SESEmailTemplate, TemplatedEmail


@receiver(post_save, sender=OneTimePassword)
def sendOneTimePasswordThroughSES(sender, instance, created, **kwargs):
    """
    OTP delivery is handled by AWS SES. This function tells AWS to send an otp email to the user,
    via registered email address.
    """
    if created:
        # Create the TemplatedEmail object and run the send function
        if instance.status == 'IDLE':
            try:

                email = TemplatedEmail.objects.create(
                    template=instance.email_template,
                    email=instance.user.email,
                    template_data={
                        'otp': instance.code,
                        'email': instance.user.email,
                    }
                )

                instance.status = 'SENT'
                instance.save()
            except Exception as e:
                instance.status = 'FAILED'
                instance.save()
                raise Exception(
                    "Error while creating TemplatedEmail object.")
            else:
                try:
                    email.send()
                except Exception as e:
                    instance.status = 'FAILED'
                    instance.save()
                else:
                    instance.status = 'DELIVERED'
                    instance.expires_at = timezone.now() + instance.expiry_time
                    instance.save()
