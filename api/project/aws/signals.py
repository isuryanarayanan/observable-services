
# Import python libraries
import os
import boto3

# Django import
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

# Local imports
from aws.models import SESEmailTemplate


@receiver(post_save, sender=SESEmailTemplate)
def create_ses_template(sender, instance, created, **kwargs):
    ses = boto3.client('ses', region_name='ap-south-1')

    if created:
        s3 = boto3.resource('s3')
        bucket_name = os.environ.get('AWS_S3_BUCKET', None)
        if bucket_name is not None:
            text_part_key = instance.template_text_part.name
            html_part_key = instance.template_html_part.name
            text_part_object = s3.Object(bucket_name, "media/"+text_part_key)
            html_part_object = s3.Object(bucket_name, "media/"+html_part_key)
            text_part = text_part_object.get()['Body'].read().decode('utf-8')
            html_part = html_part_object.get()['Body'].read().decode('utf-8')

            # Get the mode of deployment from environment variables
            mode = os.environ.get('GENIE_CONFIGURATION_KEY', None)

            ses.create_template(
                Template={
                    'TemplateName': str(mode).upper()+"-"+instance.template_identifier,
                    'SubjectPart': instance.template_subject,
                    'TextPart': text_part,
                    'HtmlPart': html_part
                }
            )
        else:
            raise Exception(
                "AWS S3 bucket name not found in environment variables")
    else:
        """Update the template in SES"""

        s3 = boto3.resource('s3')
        bucket_name = os.environ.get('AWS_S3_BUCKET', None)
        if bucket_name is not None:
            text_part_key = instance.template_text_part.name
            html_part_key = instance.template_html_part.name
            text_part_object = s3.Object(bucket_name, "media/"+text_part_key)
            html_part_object = s3.Object(bucket_name, "media/"+html_part_key)
            text_part = text_part_object.get()['Body'].read().decode('utf-8')
            html_part = html_part_object.get()['Body'].read().decode('utf-8')

            # Get the mode of deployment from environment variables
            mode = os.environ.get('GENIE_CONFIGURATION_KEY', None)

            ses.update_template(
                Template={
                    'TemplateName': str(mode).upper()+"-"+instance.template_identifier,
                    'SubjectPart': instance.template_subject,
                    'TextPart': text_part,
                    'HtmlPart': html_part
                }
            )
        else:
            raise Exception(
                "AWS S3 bucket name not found in environment variables")


@receiver(post_delete, sender=SESEmailTemplate)
def delete_ses_template(sender, instance, **kwargs):
    ses = boto3.client('ses', region_name='ap-south-1')
    mode = os.environ.get('GENIE_CONFIGURATION_KEY', None)
    ses.delete_template(
        TemplateName=str(mode).upper()+"-"+instance.template_identifier
    )
