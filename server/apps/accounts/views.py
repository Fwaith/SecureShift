import json
import random
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import EmailOTP

User = get_user_model()

# Helpers
def json_error(error, message, status=400):
    return JsonResponse({"error": error, "message": message}, status=status)

def parse_json(request: object):
    try:
        return json.loads(request.body), None
    except (json.JSONDecodeError, ValueError):
        return None, json_error("INVALID_JSON", "Request body must be valid JSON.")

def generate_otp():
    return f"{random.randint(0, 999999):06d}"

def get_authenticated_user(request):
    """Helper: return User if session is valid, else None."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return None

# Views

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """POST /api/v1/auth/register"""
    data, error_response = parse_json(request)
    if error_response:
        return error_response

    required_fields = ["username", "email", "phoneNumber", "postcode", "password"]
    missing_fields = [field for field in required_fields if not str(data.get(field, "")).strip()]
    if missing_fields:
        return json_error("VALIDATION_ERROR", "All required fields must be provided.")

    username = data["username"].strip()
    email = data["email"].strip().lower()
    phone_number = data["phoneNumber"].strip()
    postcode = data["postcode"].strip().upper()
    user_password = data["password"]

    if len(user_password) < 8:
        return json_error(
            "VALIDATION_ERROR",
            "Password must be at least 8 characters.",
        )

    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return json_error(
            "DUPLICATE_CREDENTIALS",
            "A user with the same username or email already exists.",
            status=400,
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        # create_user will hash the password, so we can pass it directly
        password=user_password,
        is_active=False,
        phone_number=phone_number,
        postcode=postcode,
    )

    my_otp = generate_otp()

    # Remove any existing OTPs for this user and create a new one
    EmailOTP.objects.filter(user=user).delete()
    EmailOTP.objects.create(
        user=user,
        otp=my_otp
    )

    load_dotenv()

    # Send the OTP to the user's email
    # Email details
    sender = os.getenv("EMAIL_ADDRESS")
    smtp_password = os.getenv("EMAIL_PASSWORD")
    receiver = email

    if not sender or not smtp_password:
        EmailOTP.objects.filter(user=user).delete()
        user.delete()
        return json_error(
            "EMAIL_NOT_CONFIGURED",
            "Email service is not configured. Please contact support.",
            status=500,
        )

    # Message
    msg = MIMEText(f"Hello, this is your OTP from secureshift: {my_otp}.")
    msg["Subject"] = "SecureShift OTP"
    msg["From"] = sender
    msg["To"] = receiver

    # Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, smtp_password)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError):
        EmailOTP.objects.filter(user=user).delete()
        user.delete()
        return json_error(
            "EMAIL_SEND_FAILED",
            "Could not send OTP email. Please try again later.",
            status=502,
        )

    return JsonResponse(
        {
            "success": True,
            "message": "Registration successful. OTP sent to your email.",
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def verify_otp(request):
    """POST /api/v1/auth/verify-otp"""
    data, error_response = parse_json(request)
    if error_response:
        return error_response

    email = str(data.get("email", "")).strip().lower()
    otp = str(data.get("otp", "")).strip()
    if not email or not otp:
        return json_error("VALIDATION_ERROR", "Email and OTP are required.")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return json_error("INVALID_OTP", "Invalid OTP or email.", status=400)

    otp_record = (
        EmailOTP.objects.filter(
            user=user,
            otp=otp,
        )
        .first()
    )

    if not otp_record:
        return json_error("INVALID_OTP", "Invalid OTP or email.", status=400)

    otp_record.delete()

    # Equivalent to the verified field in Phoebe's plan, see apps/accounts/models.py for details
    user.is_active = True
    user.save(update_fields=["is_active"])

    return JsonResponse({"success": True, "message": "Account verified successfully."})

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """POST /api/v1/auth/login"""
    data, error_response = parse_json(request)
    if error_response:
        return error_response

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not email or not password:
        return json_error("INVALID_CREDENTIALS", "Email or password incorrect", status=401)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return json_error("INVALID_CREDENTIALS", "Email or password incorrect", status=401)

    if not user.is_active or not check_password(password, user.password):
        return json_error("INVALID_CREDENTIALS", "Email or password incorrect", status=401)

    request.session["user_id"] = user.pk
    request.session.modified = True

    response = JsonResponse({"success": True, "message": "Login successful."})
    return response

@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    """POST /api/v1/auth/logout"""
    request.session.flush()
    return JsonResponse({"success": True, "message": "Logout successful."})

@csrf_exempt
@require_http_methods(["POST"])
def update_user(request):
    """
    POST /api/v1/users/me/update
    Allows an authenticated user to update their username, email,
    phone number, postcode, and/or password.

    Body (all fields optional):
    {
        "username":    "new_username",
        "email":       "new@email.com",
        "phoneNumber": "07700900000",
        "postcode":    "B76",
        "password":    "newSecurePassword123",
        "currentPassword": "requiredIfChangingPassword"
    }
    """
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse(
            {"error": "NOT_AUTHENTICATED", "message": "You must be logged in."},
            status=401,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"error": "INVALID_JSON", "message": "Request body must be valid JSON."},
            status=400,
        )

    errors = {}

    #Username
    new_username = data.get("username")
    if new_username is not None:
        new_username = new_username.strip()
        if not new_username:
            errors["username"] = "Username cannot be blank."
        elif (
            User.objects.filter(username=new_username)
            .exclude(pk=user.pk)
            .exists()
        ):
            errors["username"] = "That username is already taken."
        else:
            user.username = new_username

    #Email
    new_email = data.get("email")
    if new_email is not None:
        new_email = new_email.strip().lower()
        if not new_email:
            errors["email"] = "Email cannot be blank."
        elif (
            User.objects.filter(email=new_email)
            .exclude(pk=user.pk)
            .exists()
        ):
            errors["email"] = "An account with that email already exists."
        else:
            user.email = new_email

    #Phone number
    new_phone = data.get("phoneNumber")
    if new_phone is not None:
        user.phone_number = new_phone.strip()

    #Postcode
    new_postcode = data.get("postcode")
    if new_postcode is not None:
        user.postcode = new_postcode.strip().upper()

    #Password
    new_password = data.get("password")
    if new_password is not None:
        current_password = data.get("currentPassword")
        if not current_password:
            errors["currentPassword"] = (
                "Your current password is required to set a new one."
            )
        elif not check_password(current_password, user.password):
            errors["currentPassword"] = "Current password is incorrect."
        elif len(new_password) < 8:
            errors["password"] = "New password must be at least 8 characters."
        else:
            user.set_password(new_password)
            # Keep the session alive after password change
            request.session["user_id"] = user.pk

    if errors:
        return JsonResponse(
            {
                "error": "VALIDATION_ERROR",
                "message": "One or more fields are invalid.",
                "fields": errors,
            },
            status=400,
        )

    user.save()

    return JsonResponse(
        {
            "success": True,
            "message": "Profile updated successfully.",
            "user": {
                "userId": user.pk,
                "username": user.username,
                "email": user.email,
                "phoneNumber": user.phone_number,
                "postcode": user.postcode,
            },
        }
    )
    
@csrf_exempt
@require_http_methods(["GET"])
def users_me(request):
    """GET /api/v1/users/me"""
    if "user_id" not in request.session:
        return JsonResponse(
            {"error": "NOT_AUTHENTICATED", "message": "You must be logged in to view your profile."},
            status=401,
        )
    
    user_id = request.session["user_id"]
    
    try:
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        # Shouldn't happen, but JIC
        return JsonResponse({"error": "NOT_AUTHENTICATED", "message": "You must be logged in to view your profile."}, status=401)
        
    return JsonResponse({
            "userId": user.pk,
            "username": user.username,
            "email": user.email,
            "phoneNumber": user.phone_number,
            "postcode": user.postcode,
            "is_admin": user.is_admin,
        })

@csrf_exempt
@require_http_methods(["GET"])
def users_list(request):
    """GET /api/v1/users"""
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse(
            {"error": "NOT_AUTHENTICATED", "message": "You must be logged in."},
            status=401,
        )

    if not user.is_admin:
        return JsonResponse(
            {"error": "FORBIDDEN", "message": "Admin access is required."},
            status=403,
        )

    users = User.objects.all().order_by("id")
    payload = [
        {
            "id": each_user.pk,
            "username": each_user.username,
            "email": each_user.email,
            "level": "admin" if each_user.is_admin else "user",
        }
        for each_user in users
    ]

    # We're returning a list, bc default behaviour of JsonResponse is to expect a dict
    # But Haider has already made the FE expect a list
    return JsonResponse(payload, safe=False)
