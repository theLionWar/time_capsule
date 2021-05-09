from django.contrib import admin
from playlist_creation.models import Playlist, Track


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'source_username', 'status')
    search_fields = ['source_username', 'status']
    readonly_fields = ("created_at",)


class TrackAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'artist', 'title',)
    search_fields = ['artist', 'playlist']
    readonly_fields = ("created_at",)


admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Track, TrackAdmin)