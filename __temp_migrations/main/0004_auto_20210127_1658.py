# Generated by Django 2.2.12 on 2021-01-27 15:58

from django.db import migrations
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20210126_1729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='roll',
            field=otree.db.models.IntegerField(choices=[[0, '0'], [1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6']], default=0, null=True, verbose_name='Hodnota hodu:'),
        ),
    ]
