from django.contrib import admin
from playlist_creation.models import Playlist, Track, TrackPlaylist


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'source_providers', 'status')
    search_fields = ['status']
    readonly_fields = ("created_at",)


class TrackAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'artist', 'title',)
    search_fields = ['artist', 'playlist']
    readonly_fields = ("created_at",)


class TrackPlaylistAdmin(admin.ModelAdmin):
    list_display = ('track', 'playlist', 'source_provider',)
    search_fields = ['playlist']


admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(TrackPlaylist, TrackPlaylistAdmin)
