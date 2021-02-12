# Generated by Django 2.2.12 on 2021-02-09 20:10

from django.db import migrations
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20210208_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='hrootID',
            field=otree.db.models.StringField(max_length=10000, null=True, verbose_name='Identifikační číslo v Hroot'),
        ),
        migrations.AlterField(
            model_name='player',
            name='nationality',
            field=otree.db.models.StringField(choices=[['svk', 'slovenská'], ['czk', 'česká'], ['other', 'jiná']], max_length=10000, null=True, verbose_name='Národnost'),
        ),
    ]