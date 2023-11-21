

from django.core.management.base import BaseCommand
import random
import string
import os


# Local imports
from aws.models import SESEmailTemplate


class Command(BaseCommand):
    help = 'Create Email templates'


    def handle(self, *args, **options):
        templates_folder = os.path.join('aws', 'templates')

        # Traverses through the templates folder and creates an SESEmailTemplate object for each template folder
        for template_name in os.listdir(templates_folder):
            template_path = os.path.join(templates_folder, template_name)
            if os.path.isdir(template_path):
                template_html = os.path.join(template_path, 'template.html')
                template_text = os.path.join(template_path, 'template.txt')
                template_subject = os.path.join(template_path, 'template_subject.txt')

                with open(template_subject, 'r') as file:
                    subject = file.read().strip()

                SESEmailTemplate.objects.create(
                    template_identifier=template_name,
                    template_subject=subject,
                    template_text_part=template_text,
                    template_html_part=template_html,
                    template_keys={"otp": "otp", "email": "email"}
                )

                print(f'SESEmailTemplate object created for {template_name}.')
