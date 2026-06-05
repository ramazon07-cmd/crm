from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

phone_regex = RegexValidator( 
    regex=r'^\+?998\d{9}$',
    message="Telefon raqam formatda bo'lishi kerak: '+998901234567'"
)


class User(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        blank=False,
        null=False,
    )

    first_name = models.CharField(
        _("first name"),
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=False,
        null=False,
    )
    phone_number = models.CharField(
        _("phone number"),
        validators=[phone_regex], 
        max_length=13,
        blank=True,
        null=True,
        unique=True,
    )
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        blank=True,
        null=True,
    )
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='ADMIN',
    )
    is_verified = models.BooleanField(
        _("is verified"),
        default=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"] 

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]

    def clean(self):
        super().clean()
        if self.first_name and len(self.first_name.strip()) < 2:
            raise ValidationError({
                'first_name': "Ism kamida 2 ta harf bo'lishi kerak."
            })
        if self.last_name and len(self.last_name.strip()) < 2:
            raise ValidationError({
                'last_name': "Familiya kamida 2 ta harf bo'lishi kerak."
            })

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username