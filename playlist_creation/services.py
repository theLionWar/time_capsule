import abc
from datetime import date, datetime
from dataclasses import dataclass
import logging
from typing import ClassVar, Optional

import pylast
import tekore as tk
from django.conf import settings
from social_core.exceptions import AuthException

from playlist_creation.models import Playlist, Track, MusicProviders, TrackPlaylist

logger = logging.getLogger(__name__)

TRACKS_LIMIT_PER_PLAYLIST = 50


@dataclass
class PlaylistCreationException(Exception):
    message: str


@dataclass
class TracksProvider(abc.ABC):
    provider_user_id: str = None

    @property
    @classmethod
    @abc.abstractmethod
    def PROVIDER(cls) -> MusicProviders:
        ...

    def _create_and_save_track(self, artist: str, title: str, provider_track_id: Optional[str] = None) -> Track:
        track, _ = Track.objects.get_or_create(artist=artist, title=title)
        if provider_track_id:
            track['provider_urls'][self.provider] = provider_track_id
            track.save()
        return track

    @abc.abstractmethod
    def create_tracks(self, provider_user_id: str, from_date: date, to_date: date,
                      limit: int = 10) -> list[Track]:
        ...


@dataclass
class LastFMTracksProvider(TracksProvider):
    PROVIDER: ClassVar[MusicProviders] = MusicProviders.LASTFM

    def create_tracks(self, provider_user_id: str, from_date: date, to_date: date, limit: int = 10) -> list[Track]:
        lastfm_network = pylast.LastFMNetwork(api_key=settings.LASTFM_API_KEY, api_secret=settings.LASTFM_SHARED_SECRET)
        lastfm_user = pylast.User(user_name=provider_user_id, network=lastfm_network)

        from_date = datetime.combine(from_date, datetime.min.time())
        to_date = datetime.combine(to_date, datetime.min.time())
        try:
            lastfm_user.get_registered()
            tracks = lastfm_user.get_recent_tracks(cacheable=False, limit=limit,
                                                   time_from=int(datetime.timestamp(from_date)),
                                                   time_to=int(datetime.timestamp(to_date)))
        except pylast.PyLastError:
            logger.warning('Could not get Last.fm tracks for username ', extra={'lastfm_username': provider_user_id})
            raise PlaylistCreationException(message=f'Could not get Last.fm tracks from username: {provider_user_id}')

        # TODO: rethink this exception when we support multiple source providers
        if not tracks:
            raise PlaylistCreationException(message=f'Could not get tracks from Last.fm user: {provider_user_id}'
                                                    f' from the requested dates')

        return [self._create_and_save_track(track.track.artist.name, track.track.title) for track in tracks]


@dataclass
class SpotifyTracksProvider(TracksProvider):
    PROVIDER: ClassVar[MusicProviders] = MusicProviders.SPOTIFY

    def create_tracks(self, provider_user_id: str, from_date: date, to_date: date, limit: int = 10) -> list[Track]:
        access_token = provider_user_id
        spotify = tk.Spotify(access_token)

        to_date = datetime.combine(to_date, datetime.min.time())
        tracks = spotify.playback_recently_played(before=int(datetime.timestamp(to_date)), limit=limit)

        return [self._create_and_save_track(track.track.artists[0].name, tracks.items[0].track.title,
                                            track.track.uri) for track in tracks.items]


@dataclass
class PlaylistTargetService(abc.ABC):

    @property
    @classmethod
    @abc.abstractmethod
    def PROVIDER(cls) -> MusicProviders:
        ...

    @abc.abstractmethod
    def create_playlist(self, playlist: Playlist) -> str:
        ...


@dataclass
class SpotifyPlaylistTargetService(PlaylistTargetService):
    PROVIDER: ClassVar[MusicProviders] = MusicProviders.SPOTIFY

    def create_playlist(self, playlist: Playlist) -> str:
        if not playlist.tracks.all():
            logger.warning('Playlist has no tracks', extra={'playlist_id': playlist.id})
            raise Exception('Playlist has no tracks')
        social_user = playlist.user.social_auth.get(provider='spotify')
        access_token = social_user.extra_data.get('access_token')
        spotify = tk.Spotify(access_token)

        spotify_playlist = spotify.playlist_create(user_id=social_user.uid, name=playlist.name)

        playlist.provider_urls[self.PROVIDER] = spotify_playlist.external_urls[self.PROVIDER]
        playlist.save()

        spotify_track_uris = []
        for track in playlist.tracks.all():
            if track.provider_urls.get(self.PROVIDER):
                spotify_track_uris.append(track.provider_urls.get(self.PROVIDER))
            else:
                track_sp_data = spotify.search(query=f'artist:{track.artist} track:{track.title}', types=('track', ))
                try:
                    track_sp_uri = track_sp_data[0].items[0].uri

                    track.provider_urls[self.PROVIDER] = track_sp_uri
                    track.save()
                    spotify_track_uris.append(track_sp_uri)
                except IndexError:
                    logger.info('could not find track in Spotify', extra={'artist': track.artist, 'title': track.title,
                                                                          'track_id': track.id,
                                                                          'playlist_id': playlist.id})

        spotify.playlist_add(playlist_id=spotify_playlist.id, uris=spotify_track_uris)
        return playlist.provider_urls[self.PROVIDER]


def create_playlist_in_target(target: PlaylistTargetService, providers: list[TracksProvider],
                              playlist: Playlist) -> str:

    tracks: dict[MusicProviders, list[Track]] = {provider.PROVIDER: [] for provider in providers}
    for provider in providers:
        new_tracks: list[Track] = provider.create_tracks(provider.provider_user_id, playlist.from_date,
                                                         playlist.to_date, limit=TRACKS_LIMIT_PER_PLAYLIST)
        tracks[provider.PROVIDER].extend(new_tracks)

    for provider_enum, provider_tracks in tracks.items():
        for track in provider_tracks:
            TrackPlaylist.objects.get_or_create(track=track, playlist=playlist, source_provider=provider_enum)

    return target.create_playlist(playlist)


def create_playlist_in_target_social_pipeline(backend, user, response, *args, **kwargs):
    try:
        playlist_id = kwargs['request'].session.pop('playlist')
    except KeyError:
        logger.warning('no playlist id in session during auth pipeline')
        raise AuthException(backend, 'Missing playlist in session, please try again')

    social_user = user.social_auth.get(provider='spotify')
    try:
        playlist = Playlist.objects.get(id=playlist_id)
        playlist.user = user
        playlist.source_providers[MusicProviders.SPOTIFY] = social_user.uid
        playlist.status = Playlist.STARTED_CREATION
        playlist.save()
    except Playlist.DoesNotExist:
        logger.warning('playlist not found during auth pipeline')
        raise AuthException(backend, 'Internal playlist was not found, please try again')

    try:
        access_token = social_user.extra_data.get('access_token')

        source_providers: list[TracksProvider] = [
            LastFMTracksProvider(provider_user_id=playlist.source_providers[MusicProviders.LASTFM]),
            SpotifyTracksProvider(provider_user_id=access_token)
        ]
        playlist_url = create_playlist_in_target(target=SpotifyPlaylistTargetService(), providers=source_providers,
                                                 playlist=playlist)
    except PlaylistCreationException as e:
        raise AuthException(backend, e.message)
    except Exception as e:
        logger.warning(e)
        raise AuthException(backend, 'A general error occurred, please contact support')

    playlist.status = Playlist.FINISHED_CREATION
    playlist.save()

    kwargs['request'].session['playlist_url'] = playlist_url
