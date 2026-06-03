from django.utils import timezone

from django.db import migrations, models


def populate_existing_teachers(apps, schema_editor):
    Teacher = apps.get_model('teachers', 'Teacher')
    for index, teacher in enumerate(Teacher.objects.order_by('pk'), start=1):
        teacher.full_name = teacher.name.strip() or f'Teacher {index}'
        teacher.phone = f'+99890000000{index}'
        teacher.subject = 'General'
        teacher.salary_type = 'fixed'
        teacher.salary_value = 0
        teacher.status = 'active'
        teacher.created_at = timezone.now()
        teacher.save()


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='full_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='email',
            field=models.EmailField(
                blank=True, max_length=200, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name='teacher',
            name='subject',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='salary_type',
            field=models.CharField(
                choices=[('fixed', 'Fixed'), ('percent', 'Percent')],
                default='fixed',
                max_length=10,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacher',
            name='salary_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacher',
            name='status',
            field=models.CharField(
                choices=[('active', 'Active'), ('inactive', 'Inactive')],
                default='active',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='teacher',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teacher',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(
            populate_existing_teachers,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='full_name',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='phone',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='subject',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='name',
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='experience',
        ),
    ]
