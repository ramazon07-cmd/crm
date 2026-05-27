from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='grades')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    date = models.DateField()

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.title} - {self.score}"
