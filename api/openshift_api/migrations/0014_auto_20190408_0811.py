# Generated by Django 2.1.2 on 2019-04-08 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openshift_api', '0013_auto_20190327_0432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostinfo',
            name='volumes',
            field=models.ManyToManyField(to='openshift_api.Volume'),
        ),
    ]
