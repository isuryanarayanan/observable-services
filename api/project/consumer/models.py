from django.db import models


class Connection(models.Model):
    """
    The client will send in the refresh token they have, when the refresh token is recieved
    it is used to generate a new access token. The access token is then used to authenticate
    the user with this connection instance. 
    """

    client = models.CharField(
        max_length=255, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, null=True, blank=True)

    is_restricted = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.client}"
        else:
            return f"Unauthenticated user"

    def save(self, *args, **kwargs):
        """
        Save the model
        """
        super().save(*args, **kwargs)

        if self.is_closed:
            self.delete()

    class Meta:
        verbose_name = 'Connection'
        verbose_name_plural = 'Connections'
