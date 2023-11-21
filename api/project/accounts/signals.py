""" Signals fire when user model is created. """

# Django import
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

# Third party import
import boto3

# Local imports
from .models import User, Username, Referral
from otp.models import OneTimePassword
from aws.models import SESEmailTemplate


@receiver(post_save, sender=Username)
def createReferral(sender, instance, created, **kwargs):
    """ 
    Create a referral object when a username is created.
    """
    if created:
        Referral.objects.create(
            user=instance.user,
            code=instance.username+"#"+str(instance.tag),
        )


# @receiver(post_save, sender=User)
# def sendAWSIdentityVerification(sender, instance, created, **kwargs):
#     """ 
#     Email validation is handled by AWS SES.
#     This function tells AWS to send a verification email to the user.   
#     """
#     if created:

#         if instance.provider == 'EMAIL':

#             OneTimePassword.objects.create(
#                 user=instance,
#                 email_template=SESEmailTemplate.objects.get(
#                     template_identifier="EmailVerificationTemplate"),
#             )
