from datetime import date

from django.db import migrations, models
from django.utils import timezone


def populate_existing_students(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    for index, student in enumerate(Student.objects.order_by('pk'), start=1):
        student.phone = f'+99890000000{index}'
        student.monthly_fee = 0
        student.start_date = date(2024, 1, 1)
        student.status = 'active'
        student.created_at = timezone.now()
        student.save()


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='full_name',
            field=models.CharField(max_length=150),
        ),
        migrations.AddField(
            model_name='student',
            name='group_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='monthly_fee',
            field=models.DecimalField(
                decimal_places=2, default=0, max_digits=12
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='start_date',
            field=models.DateField(default=date(2024, 1, 1)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('inactive', 'Inactive'),
                    ('graduated', 'Graduated'),
                ],
                default='active',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(
            populate_existing_students,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.RemoveField(
            model_name='student',
            name='age',
        ),
    ]
