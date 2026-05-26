from django.db import models

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    experience = models.IntegerField()

    def __str__(self):
        return self.name