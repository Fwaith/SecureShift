from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, EmailOTP
import json


class RegisterTests(TestCase):

    def setUp(self):
        self.client = Client()

    def post(self, data):
        return self.client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )

    def test_missing_fields_returns_error(self):
        """Sending incomplete data should fail"""
        response = self.post({"username": "yahya"})
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error'], 'VALIDATION_ERROR')

    def test_short_password_rejected(self):
        """Passwords under 8 characters should be rejected"""
        response = self.post({
            "username": "yahya",
            "email": "yahya@test.com",
            "phoneNumber": "07700000000",
            "postcode": "B76",
            "password": "short"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'VALIDATION_ERROR')

    def test_duplicate_username_rejected(self):
        """Registering with an already taken username should fail"""
        User.objects.create_user(
            username='yahya', email='other@test.com', password='password123',
            is_active=True,
            postcode='B1'
        )
        response = self.post({
            "username": "yahya",
            "email": "new@test.com",
            "phoneNumber": "07700000000",
            "postcode": "B76",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'DUPLICATE_CREDENTIALS')

    def test_duplicate_email_rejected(self):
        """Registering with an already taken email should fail"""
        User.objects.create_user(
            username='other', email='yahya@test.com', password='password123',
            is_active=True,
            postcode='B1'
        )
        response = self.post({
            "username": "yahya2",
            "email": "yahya@test.com",
            "phoneNumber": "07700000000",
            "postcode": "B76",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'DUPLICATE_CREDENTIALS')


class VerifyOTPTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='yahya', email='yahya@test.com',
            password='password123', is_active=False,
            postcode='B1'
        )
        EmailOTP.objects.create(user=self.user, otp='123456')

    def post(self, data):
        return self.client.post(
            '/api/v1/auth/verify-otp',
            data=json.dumps(data),
            content_type='application/json'
        )

    def test_correct_otp_activates_account(self):
        """Valid OTP should activate the user account"""
        response = self.post({"email": "yahya@test.com", "otp": "123456"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_wrong_otp_fails(self):
        """Wrong OTP should be rejected"""
        response = self.post({"email": "yahya@test.com", "otp": "000000"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'INVALID_OTP')

    def test_wrong_email_fails(self):
        """Non-existent email should be rejected"""
        response = self.post({"email": "nobody@test.com", "otp": "123456"})
        self.assertEqual(response.status_code, 400)

    def test_missing_fields_fails(self):
        """Missing email or OTP should return error"""
        response = self.post({"email": "yahya@test.com"})
        self.assertEqual(response.status_code, 400)


class LoginTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='yahya', email='yahya@test.com',
            password='password123', is_active=True,
            postcode='B1'
        )

    def post(self, data):
        return self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )

    def test_correct_credentials_logs_in(self):
        """Valid email and password should succeed"""
        response = self.post({"email": "yahya@test.com", "password": "password123"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_wrong_password_fails(self):
        """Wrong password should return 401"""
        response = self.post({"email": "yahya@test.com", "password": "wrongpass"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['error'], 'INVALID_CREDENTIALS')

    def test_wrong_email_fails(self):
        """Non-existent email should return 401"""
        response = self.post({"email": "nobody@test.com", "password": "password123"})
        self.assertEqual(response.status_code, 401)

    def test_inactive_account_cannot_login(self):
        """Unverified (inactive) account should be rejected"""
        self.user.is_active = False
        self.user.save()
        response = self.post({"email": "yahya@test.com", "password": "password123"})
        self.assertEqual(response.status_code, 401)

    def test_missing_fields_fails(self):
        """Missing email or password should fail"""
        response = self.post({"email": "yahya@test.com"})
        self.assertEqual(response.status_code, 401)


class LogoutTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='yahya', email='yahya@test.com',
            password='password123', is_active=True,
            postcode='B1'
        )

    def test_logout_clears_session(self):
        """Logging out should clear the session"""
        session = self.client.session
        session['user_id'] = self.user.pk
        session.save()

        response = self.client.post('/api/v1/auth/logout',
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('user_id', self.client.session)


class UsersMeTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='yahya', email='yahya@test.com',
            password='password123', is_active=True,
            postcode='B1'
        )

    def test_authenticated_user_gets_profile(self):
        """Logged in user should get their profile info"""
        session = self.client.session
        session['user_id'] = self.user.pk
        session.save()

        response = self.client.get('/api/v1/users/me',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'yahya')
        self.assertEqual(data['email'], 'yahya@test.com')

    def test_unauthenticated_returns_401(self):
        """No session should return 401"""
        response = self.client.get('/api/v1/users/me',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)


class UpdateUserTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='yahya', email='yahya@test.com',
            password='password123', is_active=True,
            postcode='B1'
        )
        session = self.client.session
        session['user_id'] = self.user.pk
        session.save()

    def post(self, data):
        return self.client.post(
            '/api/v1/users/me/update',
            data=json.dumps(data),
            content_type='application/json'
        )

    def test_update_username_success(self):
        """Should be able to change username"""
        response = self.post({"username": "yahya_new"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'yahya_new')

    def test_update_email_success(self):
        """Should be able to change email"""
        response = self.post({"email": "new@test.com"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@test.com')

    def test_duplicate_username_rejected(self):
        """Cannot change to a username that already exists"""
        User.objects.create_user(
            username='taken', email='taken@test.com',
            password='password123', is_active=True,
            postcode='B1'
        )
        response = self.post({"username": "taken"})
        self.assertEqual(response.status_code, 400)

    def test_password_change_requires_current_password(self):
        """Changing password without providing current password should fail"""
        response = self.post({"password": "newpassword123"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'VALIDATION_ERROR')

    def test_password_change_wrong_current_password(self):
        """Wrong current password should be rejected"""
        response = self.post({
            "password": "newpassword123",
            "currentPassword": "wrongpassword"
        })
        self.assertEqual(response.status_code, 400)

    def test_password_change_success(self):
        """Correct current password should allow password change"""
        response = self.post({
            "password": "newpassword123",
            "currentPassword": "password123"
        })
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_update_fails(self):
        """Not logged in should return 401"""
        self.client.session.flush()
        response = self.post({"username": "hacker"})
        self.assertEqual(response.status_code, 401)