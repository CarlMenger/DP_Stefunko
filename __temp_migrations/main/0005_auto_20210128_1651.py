# Generated by Django 2.2.12 on 2021-01-28 15:51

from django.db import migrations
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210127_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='roll',
            field=otree.db.models.IntegerField(choices=[[1, '1'], [2, '2'], [3, '3'], [4, '4'], [5, '5'], [6, '6']], default=0, null=True, verbose_name='Hodnota hodu:'),
        ),
    ]
