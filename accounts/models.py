from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def mark_as_deleted(self):
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True


# Create your models here.
class CustomUserManager(BaseUserManager):
    """
    Custom User Model Manager where email ins e unique indetifier
    for authentication instead of the username
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User require an email field")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    """
    Custom User model
    """

    username = models.CharField(max_length=100, unique=True, blank=True)
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    userpic = models.ImageField(upload_to="userpics/", blank=True, null=True)
    bio = models.CharField(blank=True, null=True, max_length=100)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta, BaseModel.Meta):
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.email}"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.generate_unique_username()
        super().save(*args, **kwargs)

    def generate_unique_username(self):
        base_username = slugify(self.get_full_name() or self.email.split("@")[0])
        username = base_username
        iteration = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}-{iteration}"
            iteration += 1

        return username

    def get_absolute_url(self):
        return reverse("profile_view", kwargs={"username": self.username})

    def get_userpic_url(self):
        if self.userpic:
            return f"{self.userpic.url}"
        return "/static/img/default_userpic.webp"
