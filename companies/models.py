from django.db import models
from django.utils.text import slugify

from accounts.models import BaseModel
# Create your models here.


class Company(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)


class CompanyMemership(BaseModel):
    class RoleChoices(models.TextChoices):
        OWNER = "owner"
        ADMIN = "admin"
        STAFF = "staff"
        VIEWER = "viewer"

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="company_memberships"
    )
    role = models.CharField(
        max_length=10, choices=RoleChoices.choices, default=RoleChoices.VIEWER
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Company Membership"
        verbose_name_plural = "Company Memberships"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.company} - {self.role}"
