from django.apps import AppConfig


class AwsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aws'

    def ready(self):
        from aws import signals
