# Generated by Django 3.2.2 on 2021-05-06 21:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UUIDModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('uuidmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='playlist_creation.uuidmodel')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source', models.CharField(choices=[('lastfm', 'Last.fm')], default='lastfm', max_length=256)),
                ('source_username', models.CharField(max_length=256)),
                ('from_date', models.DateField(default=None, null=True)),
                ('to_date', models.DateField(default=None, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Initiated'), (1, 'Started creation'), (2, 'Finished creation')], default=0)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='playlists', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('playlist_creation.uuidmodel', models.Model),
        ),
    ]