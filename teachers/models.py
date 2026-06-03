from django.db import models


class Teacher(models.Model):
    SALARY_TYPE_CHOICES = [
        ('fixed', 'Fixed'),
        ('percent', 'Percent'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=200, unique=True, blank=True, null=True)
    subject = models.CharField(max_length=100)
    salary_type = models.CharField(max_length=10, choices=SALARY_TYPE_CHOICES)
    salary_value = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
