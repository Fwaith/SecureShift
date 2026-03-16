from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Instead of making a verified: bool field, we just use is_active (default field) to indicate if the user has verified their email.
    
    phone_number = models.CharField(max_length=20, blank=True, default='')
    postcode = models.CharField(max_length=10, blank=True, default='')

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_set',
        blank=True
    )

    def __str__(self):
        return self.username

class EmailOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_otps',
    )
    otp = models.CharField(max_length=6)

    def __str__(self):
        return f"OTP for {self.user.email}"