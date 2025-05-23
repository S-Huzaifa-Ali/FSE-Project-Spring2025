# Generated by Django 5.2 on 2025-05-06 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Candidate', '0002_resume'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='resume',
        ),
        migrations.AddField(
            model_name='candidate',
            name='education',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='experience',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='candidate',
            name='skills',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='age',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='qualification',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
