import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields, JSONField


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Playlist(UUIDModel, TimeStampMixin):
    LASTFM = 'lastfm'
    SOURCE_PLATFORMS = [
        (LASTFM, 'Last.fm'),
    ]

    INITIATED = 0
    STARTED_CREATION = 1
    FINISHED_CREATION = 2
    PLAYLIST_STATUS = [
        (INITIATED, 'Initiated'),
        (STARTED_CREATION, 'Started creation'),
        (FINISHED_CREATION, 'Finished creation'),
    ]

    user = models.ForeignKey(User, related_name='playlists', null=True, on_delete=models.SET_NULL)
    source = fields.CharField(max_length=256, choices=SOURCE_PLATFORMS, default=LASTFM)
    source_username = fields.CharField(max_length=256)
    from_date = fields.DateField(null=True, default=None)
    to_date = fields.DateField(null=True, default=None)
    status = fields.PositiveSmallIntegerField(choices=PLAYLIST_STATUS, default=INITIATED)

    @property
    def name(self):
        return f'Time Capsule: {str(self.from_date)} - {str(self.to_date)}'


class Track(UUIDModel, TimeStampMixin):
    artist = fields.CharField(max_length=256)
    title = fields.CharField(max_length=256)
    provider_urls = JSONField(default=dict)
    playlists = models.ManyToManyField(Playlist, related_name='tracks')
