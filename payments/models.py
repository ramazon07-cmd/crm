from django.db import models
from django.utils import timezone
from students.models import Student


class Payment(models.Model):
    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['student', 'month']

    def __str__(self):
        return f"{self.student.full_name} - {self.month} - {self.status}"

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = Payment.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        if self.status == self.Status.PAID and old_status != self.Status.PAID:
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)
