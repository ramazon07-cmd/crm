from django.db import models
from django.core.exceptions import ValidationError

class Student(models.Model):
    full_name = models.CharField(max_length=200)
    age = models.IntegerField()

    def __str__(self):
        return self.full_name

    def clean(self):  # ✅ QO'SHILDI
        super().clean()
        if self.age < 5 or self.age > 100:
            raise ValidationError({
                'age': "Yosh 5 va 100 orasida bo'lishi kerak."
            })
        if len(self.full_name.strip()) < 3:
            raise ValidationError({
                'full_name': "To'liq ism kamida 3 ta harf bo'lishi kerak."
            })