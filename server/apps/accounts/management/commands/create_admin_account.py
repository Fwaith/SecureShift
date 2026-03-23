from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a default admin account for local/testing use."

    def handle(self, *args, **options):
        User = get_user_model()
        email = "admin@secureshift.com"
        password = "test1234"

        user = User.objects.filter(email=email).first()
        if user is None:
            username = "admin"
            if User.objects.filter(username=username).exists():
                username = "secureshift_admin"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True,
                is_admin=True,
                postcode="B76",
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin account: {user.email}"))
            return

        user.set_password(password)
        user.is_active = True
        user.is_admin = True
        user.save(update_fields=["password", "is_active", "is_admin"])

        self.stdout.write(self.style.SUCCESS(f"Updated admin account: {user.email}"))
