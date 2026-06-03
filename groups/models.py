from django.db import models

from teachers.models import Teacher


class Group(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=100, unique=True)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        related_name='groups',
    )
    schedule = models.JSONField(
        blank=True,
        null=True,
        help_text='Lesson days: [1,3,5] = Monday, Wednesday, Friday',
    )
    start_time = models.TimeField()
    capacity = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
