from django.db import models

class Student(models.Model):
    full_name = models.CharField(max_length=200)
    age = models.IntegerField()

    def __str__(self):
        return self.full_name