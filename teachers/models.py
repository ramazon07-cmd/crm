from django.db import models
from django.core.exceptions import ValidationError

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    experience = models.IntegerField()

    def __str__(self):
        return self.name

    def clean(self):  # ✅ QO'SHILDI
        super().clean()
        if self.experience < 0:
            raise ValidationError({
                'experience': "Tajriba manfiy bo'lishi mumkin emas."
            })
        if self.experience > 60:
            raise ValidationError({
                'experience': "Tajriba 60 yildan oshmasligi kerak."
            })