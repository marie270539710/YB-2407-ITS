# Generated by Django 5.1.6 on 2025-03-18 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('navigation', '0005_availableslots'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slots', models.TextField(verbose_name='Available Slots')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='AvailableSlots',
        ),
    ]
