# Generated by Django 2.1.2 on 2019-06-11 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openshift_api', '0029_package_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='logo',
        ),
        migrations.AddField(
            model_name='cluster',
            name='status',
            field=models.CharField(choices=[('RUNNING', 'running'), ('INSTALLING', 'installing'), ('UNKNOWN', 'unknown'), ('ERROR', 'error'), ('WARNING', 'warning')], default='UNKNOWN', max_length=128),
        ),
    ]