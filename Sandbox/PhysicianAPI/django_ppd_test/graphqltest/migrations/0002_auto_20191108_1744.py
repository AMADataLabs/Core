# Generated by Django 2.2.7 on 2019-11-08 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('graphqltest', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='djangotest',
            options={'managed': False, 'ordering': ('me',)},
        ),
    ]
