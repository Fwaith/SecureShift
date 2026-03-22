from django.contrib.auth.models import AbstractUser
from django.db import models
from django.apps import apps

def _extract_outcode(postcode):
	if not postcode:
		return None

	normalized = postcode.strip().upper()
	if not normalized:
		return None

	parts = normalized.split()
	if len(parts) > 1:
		return parts[0]

	compact = "".join(parts)
	if len(compact) > 3:
		return compact[:-3]

	return compact

class User(AbstractUser):
    # Instead of making a verified: bool field, we just use is_active (default field) to indicate if the user has verified their email.
    
    phone_number = models.CharField(max_length=20, blank=True, default='')
    postcode = models.CharField(max_length=10, blank=True, default='')
    neighborhood = models.ForeignKey(
        'habitability.Neighborhood',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )

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

    # Overrides save to automatically create or link a Neighborhood based on the postcode
    # Hack to fix original implementation of user creation
    # In which user's neighbourhood was simply a strng
    def save(self, *args, **kwargs):
        # CLean postcode
        postcode = _extract_outcode(self.postcode)
        self.postcode = postcode

        if postcode:
            neighborhood = None
            Neighborhood = apps.get_model('habitability', 'Neighborhood')

            neighborhood = (
                Neighborhood.objects.filter(postcode=postcode)
                .order_by('neighborhood_id')
                .first()
            )

            if neighborhood is None:
                # Means we haven;t found a neighbourhood w this postcode, so we create one
                # TODO: Use an API to get actual neighbourhood name?
                neighborhood_name = postcode
                    
                neighborhood = Neighborhood.objects.create(
                    neighborhood_name=neighborhood_name,
                    postcode=postcode,
                )

            self.neighborhood = neighborhood

        super().save(*args, **kwargs)

class EmailOTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_otps',
    )
    otp = models.CharField(max_length=6)

    def __str__(self):
        return f"OTP for {self.user.email}"