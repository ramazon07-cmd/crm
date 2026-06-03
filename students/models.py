from django.db import models


class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    # TODO: Replace with ForeignKey('groups.Group', ...) when groups app exists
    group_id = models.IntegerField(null=True, blank=True)
    monthly_fee = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
