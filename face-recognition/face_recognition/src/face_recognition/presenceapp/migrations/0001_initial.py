# Generated by Django 2.0.7 on 2018-07-22 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FacePresenceHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('face_id', models.BigIntegerField()),
                ('workstation_id', models.CharField(max_length=36)),
                ('minute_slot', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_seen_at', models.DateTimeField(auto_now=True)),
                ('seen_times', models.SmallIntegerField(default=1)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='facepresencehistory',
            unique_together={('workstation_id', 'face_id', 'minute_slot')},
        ),
        migrations.AlterIndexTogether(
            name='facepresencehistory',
            index_together={('workstation_id', 'created_at')},
        ),
    ]
