import boto3
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings


class SESBackend(BaseEmailBackend):
    """
    Sends mail through Amazon SES.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_SES_REGION
        )

    def send_messages(self, email_messages):
        for message in email_messages:
            self.client.send_email(
                Destination={
                    'ToAddresses': message.to,
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': message.body,
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': message.subject,
                    },
                },
                Source=message.from_email,
            )
            