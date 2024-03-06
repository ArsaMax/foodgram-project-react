# Generated by Django 3.2.3 on 2024-03-05 15:57

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_follow_cannt follow themselves'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(('user', django.db.models.expressions.F('following')), _negated=True), name='cannt follow themselves'),
        ),
    ]
