from django.conf import settings
from django.db import models

from groups.models import Group
from students.models import Student


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='attendances'
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='attendances'
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances',
    )
    note = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('student', 'date')]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"


class Holiday(models.Model):
    TYPE_CHOICES = [
        ('national', 'National'),
        ('custom', 'Custom'),
    ]

    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    recurring = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.date}"
