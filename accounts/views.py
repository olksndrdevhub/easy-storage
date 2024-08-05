import re

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import User


def email_is_valid_with_regex(email: str):
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False
    return True


def value_is_available(field_value: str, field_name: str, model: type):
    if model.objects.filter(**{field_name: field_value}).exists():
        return False
    return True


def signout_view(request):
    """
    Just Sign Out view
    """
    logout(request)
    response = redirect("signin_view")
    messages.add_message(request, messages.WARNING, "You was sign out!")
    return response


def signin_view(request):
    """
    Sign In Page
    """

    context = {}
    if request.user.is_authenticated:
        return redirect("dashboard")
    template_name = "signin.html"

    response = render(request, template_name, context)

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # check if user exists
        if not User.objects.filter(email=email).exists():
            messages.add_message(
                request,
                messages.ERROR,
                "User with this email does not exists, please Sign up",
            )
        else:
            user = authenticate(email=email, password=password)
            # handle deleted users
            if user and user.deleted:
                messages.add_message(
                    request,
                    messages.WARNING,
                    "Your account was deleted, you can restore it here.",
                )
                response = redirect("restore_account_view")
                return response
            if user is not None:
                login(request, user)

                messages.add_message(
                    request, messages.SUCCESS, "You successfully log in!"
                )
                response = redirect("dashboard")
                return response
            messages.add_message(
                request,
                messages.ERROR,
                "Wrong password...",
            )

        response["HX-Retarget"] = "form"
        response["HX-Reselect"] = "form"

    return response


def registration_view(request):
    """
    Register Page
    """
    context = {}
    template_name = "registration.html"
    if request.method == "POST":
        print(request.POST)
        first_name = request.POST.get("first_name")
        if first_name is None or first_name.strip() == "":
            messages.add_message(
                request, messages.ERROR, "First Name can not be empty!"
            )
            context["fname_error"] = "First Name can not be empty!"
        else:
            first_name = first_name.strip()
            context["submitted_f_name"] = first_name
        last_name = request.POST.get("last_name").strip()
        if last_name is None or last_name.strip() == "":
            messages.add_message(request, messages.ERROR, "Last Name can not be empty!")
            context["lname_error"] = "Last Name can not be empty!"
        else:
            last_name = last_name.strip()
            context["submitted_l_name"] = last_name
        email = request.POST.get("email").strip()
        if email is not None:
            email = email.strip()
            context["submitted_email"] = email
        if not email_is_valid_with_regex(email):
            messages.add_message(request, messages.ERROR, "Email is not valid!")
            context["email_error"] = "Email is not valid!"
        if User.objects.filter(email=email).exists():
            messages.add_message(
                request,
                messages.ERROR,
                "User with email already exists, please Sign in!",
            )
            context["email_error"] = (
                "User with this email already exists, please Sign in!"
            )
        else:
            password = request.POST.get("password")
            if password is not None:
                password = password.strip()
            try:
                validate_password(
                    password,
                )
            except forms.ValidationError as errors:
                for error in errors:
                    messages.add_message(request, messages.ERROR, f"Error: {error}")
                context["password_error"] = "Password is not valid!"
            else:
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.set_password(password)
                user.is_active = True
                user.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Registration success! You can log in now!",
                )
                response = HttpResponse()
                response["HX-Location"] = reverse("signin_view")
                return response
    return render(request, template_name, context)


def forgot_password_view(request):
    """
    Forgot Password Page
    """
    context = {}
    template_name = "forgot-password.html"
    if request.method == "POST":
        email = request.POST.get("email")
        context["submitted_email"] = email
        if not User.objects.filter(email=email).exists():
            messages.add_message(
                request,
                messages.ERROR,
                "User with email does not exists, please Sign up!",
            )
            context["email_error"] = (
                "User with this email does not exists, please Sign up!"
            )
        else:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uuid = urlsafe_base64_encode(force_bytes(user.id))
            reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uuid}/{token}/"
            print("send email confirmation")
            try:
                send_mail(
                    "Reset Password",
                    f"Click the following link to reset your password: {reset_link}.\nIf you did not request a password reset, please ignore this email.",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                context["success"] = True
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Success, check your email!",
                )
            except Exception as e:
                print(e)
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Error while sending email...",
                )
    return render(request, template_name, context)


def reset_password_view(request, uuid64, token):
    """
    Reset Password Page
    """
    context = {}
    template_name = "reset-password.html"

    try:
        uid = force_str(urlsafe_base64_decode(uuid64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.add_message(request, messages.ERROR, "Invalid link, probably expired!")
        return redirect("signin_view")

    if request.method == "POST":
        password = request.POST.get("password")
        try:
            validate_password(
                password,
            )
        except forms.ValidationError as errors:
            for error in errors:
                messages.add_message(request, messages.ERROR, f"Error: {error}")
            context["password_error"] = "Password is not valid!"
        else:
            password_confirm = request.POST.get("password_confirm")
            if password != password_confirm:
                messages.add_message(request, messages.ERROR, "Passwords do not match!")
                context["password_error"] = "Passwords do not match!"
                context["password_confirm_error"] = "Passwords do not match!"
            else:
                user.set_password(password)
                user.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Password changed successfully!",
                )
                context["success"] = True

    context["uuid64"] = uuid64
    context["token"] = token
    return render(request, template_name, context)


@login_required
def hx_change_password(request):
    template_name = "settings.html"
    context = {}
    if request.method == "POST" and request.htmx:
        data = request.POST
        print(data)
        user = request.user
        old_password = data.get("password")
        if not user.check_password(old_password):
            context["password_error"] = "Current password is wrong!"
            messages.add_message(request, messages.ERROR, "Current password is wrong!")
        new_password = data.get("new_password")
        try:
            validate_password(
                new_password,
            )
        except forms.ValidationError as errors:
            context["new_password_error"] = "New password is not valid!"
            for error in errors:
                messages.add_message(request, messages.ERROR, f"Error: {error}")
        else:
            password_confirm = data.get("password_confirm")
            if new_password != password_confirm:
                messages.add_message(request, messages.ERROR, "Passwords do not match!")
                context["new_password_error"] = "Passwords do not match!"
                context["password_confirm_error"] = "Passwords do not match!"
            else:
                # user.set_password(new_password)
                # user.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Password changed successfully!",
                )

    response = render(request, template_name, context)
    return response


def hx_send_verification_mail(request):
    """
    Send Email Verification View
    """
    if request.htmx:
        user = request.user
        if user.email_verified:
            messages.add_message(
                request,
                messages.ERROR,
                "Email already verified!",
            )
            return HttpResponse(status=200)
        token = default_token_generator.make_token(user)
        uuid = urlsafe_base64_encode(force_bytes(user.id))
        reset_link = (
            f"{request.scheme}://{request.get_host()}/verify-email/{uuid}/{token}/"
        )
        print("send email confirmation")
        try:
            send_mail(
                "Verify Email",
                f"Click the following link to verify your email: {reset_link}.\nIf you did not request email verification, please ignore this email.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                "Success, check your email inbox and spam folders!",
            )
        except Exception as e:
            print(e)
            messages.add_message(
                request,
                messages.ERROR,
                "Error while sending email...",
            )
    return HttpResponse(status=200)


def verify_email(request, uuid64: str, token: str):
    """
    Verify Email View
    """
    context = {}
    template_name = "email-verified.html"
    try:
        uid = force_str(urlsafe_base64_decode(uuid64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is None or not default_token_generator.check_token(user, token):
        context["success"] = False
    else:
        user.email_verified = True
        user.save()
        context["success"] = True
    return render(request, template_name, context)
