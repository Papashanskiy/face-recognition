# Generated by Django 2.0.7 on 2018-11-01 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recognitionapp', '0002_facephoto_wh'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='providerid',
            unique_together={('inner_id', 'provider')},
        ),
    ]