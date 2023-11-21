""" App for managing one time passwords. """

# Django import
from django.db import models
from django.utils import timezone

# Native imports
import random
import string


# Local imports
from accounts.models import User

OTP_STATUS_CHOICES = (
    ('IDLE', 'Idle'),
    ('SENT', 'Sent'),
    ('DELIVERED', 'Delivered'),
    ('FAILED', 'Failed'),
    ('EXPIRED', 'Expired'),
    ('CONSUMED', 'Consumed'),
    ('COMPLETED', 'Completed'),
    ('INVALIDATED', 'Invalidated'),
)


def validateUserWithOTP(code, user_id, template):
    """
    Validates the OTP by checking if the code matches the latest OTP of the user and is not expired.
    """

    success = False
    ghost_code = None
    otp_obj = None

    try:

        # Get all the otp objects which are DELIVERED of the user
        otps = OneTimePassword.objects.filter(
            user=user_id, status='DELIVERED', email_template=template)

        # Loop through each otp object if they have expired change status to EXPIRED,
        # if code match with any of the otp object invalidate the rest and update the
        # status to CONSUMED of the matched otp object.
        for otp in otps:
            if otp.expires_at < timezone.now():
                otp.status = 'EXPIRED'
            elif otp.code == code:
                otp.status = 'CONSUMED'
                ghost_code = otp.ghost_code
                otp_obj = otp
                success = True

            otp.save()

    except Exception as e:
        raise e

    return success, ghost_code, otp_obj


def validateActionWithGhostCode(ghost_code, otp):
    """
    Validates the action with the ghost code. And invalidates any otp if 
    the status is consumed.
    """

    success = False

    # Get all the otp objects which are CONSUMED of the user
    otps = OneTimePassword.objects.filter(
        user=otp.user, status='CONSUMED', email_template=otp.email_template)

    # Loop through all of the otps and check if the ghost code matches with any of the otps,
    # if it matches invalidate the rest of the otps.
    for otp in otps:
        if otp.ghost_code == ghost_code and success == False:
            otp.status = 'COMPLETED'
            success = True

        otp.save()

    for otp in otps:
        if otp.status != 'COMPLETED':
            otp.status = 'INVALIDATED'
            otp.save()

    return success


class OneTimePassword(models.Model):
    """
    One time passwords are used to access protected routes.
    """

    # This otp object can only be associated with this user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # Email template
    email_template = models.ForeignKey(
        'aws.SESEmailTemplate',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Status of the otp is updated by subscription and the effective functionality is decided by this field.
    status = models.CharField(
        max_length=25,
        choices=OTP_STATUS_CHOICES,
        default='IDLE'
    )

    # This is the code that is sent to the user, it is a 6 digit alphanumeric code.
    code = models.CharField(
        max_length=6,
        default='',
        unique=True
    )

    # This is the ghost coded that is only given to the user, if they successfully consume the otp.
    # It is used to perform an action associated with this otp
    ghost_code = models.CharField(
        max_length=6,
        default='',
        unique=True
    )

    # Timing flags
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    expires_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DurationField(
        default=timezone.timedelta(minutes=5)
    )

    def __str__(self) -> str:
        return f'{self.user.email} OTP | {self.status} | {self.code} | {self.expires_at} | {self.expiry_time}'

    def __generate_otp(self) -> str:
        """
        Generates a 6 digit random string as the OTP and sets the expiration time
        """
        self.code = ''.join([random.choice(string.digits) for n in range(6)])
        self.expires_at = timezone.now() + self.expiry_time
        return self.code

    def __generate_ghost_code(self) -> str:
        """
        Generates a 6 digit random string as the ghost code
        """
        self.ghost_code = ''.join(
            [random.choice(string.digits) for n in range(6)])
        return self.ghost_code

    def is_valid(self) -> bool:
        """
        Returns True if the OTP is valid and not expired or invalid.
        """
        return self.status == 'DELIVERED' and self.expires_at > timezone.now() and self.status != 'INVALIDATED'

    def regenerate_otp(self) -> str:
        """
        Resends the OTP and invalidates the previous OTP by setting its expiration time to the current time
        """
        self.status = 'INVALIDATED'
        self.expires_at = timezone.now()

    def check_ghost_code(self, ghost_code) -> bool:
        """
        Checks if the ghost code is valid, returns true and completes the OTP if it is valid
        """
        if self.ghost_code == ghost_code:
            self.status = 'COMPLETED'
            self.save()
            return True
        return False

    def save(self, *args, **kwargs):
        """ Save the otp. """
        if self.pk is None:
            self.code = self.__generate_otp()
            self.ghost_code = self.__generate_ghost_code()

        super().save(*args, **kwargs)

    class Meta:
        """ Meta class for OTP. """
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
