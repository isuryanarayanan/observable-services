""" 
User model.

Using the Django User model as a base model, we extend it to add more fields to it.
Also the BaseUserManager acts as a manager for the User model. It is used to create
a user. The create_user method creates a normal user. The create_superuser method
creates a superuser.
"""

# Django imports
from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
)
from django.contrib.auth.base_user import BaseUserManager
import random
from utils.errors import BadRequestError
from django.conf import settings


USER_PROVIDERS = (
    ('EMAIL', 'email'),
    ('GOOGLE', 'google'),
)


class UserManager(BaseUserManager):
    """ Manager for the User model """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the email and password."""

        # Check if email is provided
        if not email:
            raise ValueError('The email must be set')

        # Check if email is valid with EmailField if not return bad request
        try:
            if not self.model._meta.get_field('email').clean(email, None):
                raise ValueError('The email is not valid')
        except Exception:
            raise BadRequestError('The email is not valid')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_email_user(self, email=None, password=None, **extra_fields):
        """ Method to create a email user """
        extra_fields.setdefault(
            'is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_dob_verified', True)
        return self._create_user(email, password, **extra_fields)

    def create_social_user(self, email=None, provider=None, **extra_fields):
        """ Method to create a social user """
        extra_fields.setdefault(
            'is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('is_policies_accepted', True)
        extra_fields.setdefault('is_dob_verified', False)
        extra_fields.setdefault('provider', provider)

        password = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        """ Method to create a super user """

        extra_fields.setdefault(
            'is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """ User Abstract model """

    # Information
    email = models.EmailField(unique=True)
    dob = models.DateField(null=True, blank=True)
    username = None

    # Credentials
    is_email_verified = models.BooleanField(default=False)
    is_policies_accepted = models.BooleanField(default=False)
    is_dob_verified = models.BooleanField(default=False)

    provider = models.CharField(
        choices=USER_PROVIDERS, default='EMAIL', max_length=240, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def is_valid_password(password):
        return len(password) >= 8

    def is_valid_user(self):
        basic_checks = (
            self.is_email_verified and self.is_dob_verified)
        if_username = (self.username is not None)
        return basic_checks and if_username

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


class Username(models.Model):
    """
    Username model.

    The username in this model will also be associated with a 4 digit number.
    This number will be auto generated. The username and the tag should be unique
    together but not individually.
    """

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='username'
    )

    username = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    tag = models.CharField(
        max_length=4,
        blank=True,
        null=True
    )

    def __str__(self):
        """
        Return the username and tag.
        """
        return f'{self.username}#{self.tag} of {self.user.email}'

    def save(self, *args, **kwargs):
        """
        Save the username.

        Username shouldnt start with a number or a special character.
        It can only contain letters, numbers, and underscores.
        Also the username will not allow uppercase letters.
        """

        # Auto generate the tag until it is unique together with the username.
        while True and self.pk is None:
            self.tag = str(random.randint(1000, 9999))
            if not Username.objects.filter(username=self.username, tag=self.tag).exists():
                break

        # Check if the username starts with a number or a special character.
        if self.username[0].isdigit() or self.username[0] in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '|', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']:
            raise ValueError(
                'Username cannot start with a number or a special character.')


        # Check if the username contains any special characters.
        if not self.username.isalnum():
            raise ValueError('Username cannot contain special characters.')

        super().save(*args, **kwargs)

    class Meta:
        """
        Meta class.
        """
        unique_together = ('username', 'tag')



class Referral(models.Model):
    """
    Referral model.

    This model will be used to store the referral code and the user that
    created it. This will be created if a user signed up with a code.
    """

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='referral'
    )

    code = models.CharField(
        max_length=35,
        null=True,
        blank=True,
        unique=True
    )

    def __str__(self):
        """
        Return the code.
        """
        return f"{self.code} - {self.user.email}"

    def save(self, *args, **kwargs):
        """
        Save the referral code.

        Referral code should be 35 characters long.
        """
        if len(self.code) >= 35:
            raise ValueError(
                'Referral code should be less than 35 characters long.')

        super().save(*args, **kwargs)

    class Meta:
        """
        Meta class.
        """
        verbose_name = "referral"
        verbose_name_plural = "referrals"
        unique_together = ('user', 'code')


class Referred(models.Model):
    """
    Referred model.

    This model will be used to store the user that was referred by a code.
    """

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='referred'
    )

    referral = models.ForeignKey(
        'accounts.Referral',
        on_delete=models.CASCADE,
        related_name='referred',
    )

    def __str__(self):
        """
        Return the code.
        """
        return f"{self.referral.code} - {self.user.email}"

    def save(self, *args, **kwargs):
        """
        Save the referred user.

        Referred user should be unique.
        """
        if Referred.objects.filter(user=self.user).exists():
            raise ValueError('User has already been referred.')

        super().save(*args, **kwargs)

    class Meta:
        """
        Meta class.
        """
        verbose_name = "referred"
        verbose_name_plural = "referreds"
