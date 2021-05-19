import uuid
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields, JSONField


class MusicProviders(str, Enum):
    SPOTIFY = 'spotify'
    LASTFM = 'last.fm'

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Playlist(UUIDModel, TimeStampMixin):
    INITIATED = 0
    STARTED_CREATION = 1
    FINISHED_CREATION = 2
    PLAYLIST_STATUS = [
        (INITIATED, 'Initiated'),
        (STARTED_CREATION, 'Started creation'),
        (FINISHED_CREATION, 'Finished creation'),
    ]

    user = models.ForeignKey(User, related_name='playlists', null=True, on_delete=models.SET_NULL)
    source_providers = JSONField(default=dict)
    from_date = fields.DateField(null=True, default=None)
    to_date = fields.DateField(null=True, default=None)
    status = fields.PositiveSmallIntegerField(choices=PLAYLIST_STATUS, default=INITIATED)
    provider_urls = JSONField(default=dict)

    @property
    def name(self):
        return f'Time Capsule: {str(self.from_date)} - {str(self.to_date)}'

    def __str__(self):
        return f'{self.user.username if self.user else "no user"}: {str(self.from_date)} - {str(self.to_date)}'


class Track(UUIDModel, TimeStampMixin):
    artist = fields.CharField(max_length=256)
    title = fields.CharField(max_length=256)
    provider_urls = JSONField(default=dict)
    playlists = models.ManyToManyField(Playlist, through='TrackPlaylist', related_name='tracks')

    def __str__(self):
        return f'{self.artist} - {self.title}'


class TrackPlaylist(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    source_provider = models.CharField(max_length=256, choices=[(tag, tag.value) for tag in MusicProviders])

    class Meta:
        unique_together = ('track', 'playlist')
