import json
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

User = get_user_model()


def get_authenticated_user(request):
    """Helper: return User if session is valid, else None."""
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        return None


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