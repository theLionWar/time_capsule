import abc
from datetime import date, datetime
from dataclasses import dataclass
import logging
import pylast
import tekore as tk
from django.conf import settings
from social_core.exceptions import AuthException

from playlist_creation.models import Playlist, Track

logger = logging.getLogger(__name__)

TRACKS_LIMIT_PER_PLAYLIST = 50


@dataclass
class PlaylistCreationException(Exception):
    message: str


@dataclass
class TracksProvider(abc.ABC):

    @abc.abstractmethod
    def get_tracks(self, provider_user_id: str, from_date: date, to_date: date, limit: int = 10) -> list:
        ...


@dataclass
class LastFMTracksProvider(TracksProvider):

    def get_tracks(self, provider_user_id: str, from_date: date, to_date: date, limit: int = 10) -> list:
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

        if not tracks:
            raise PlaylistCreationException(message=f'Could not get tracks from Last.fm user: {provider_user_id}'
                                                    f' from the requested dates')

        return [(track.track.artist.name, track.track.title) for track in tracks]


@dataclass
class PlaylistTargetService(abc.ABC):

    @abc.abstractmethod
    def create_playlist(self, playlist: Playlist) -> bool:
        ...


@dataclass
class SpotifyPlaylistTargetService(PlaylistTargetService):

    def create_playlist(self, playlist: Playlist) -> bool:
        if not playlist.tracks.all():
            logger.warning('Playlist has no tracks', extra={'playlist_id': playlist.id})
            raise Exception('Playlist has no tracks')
        social_user = playlist.user.social_auth.get(provider='spotify')
        access_token = social_user.extra_data.get('access_token')
        spotify = tk.Spotify(access_token)

        spotify_playlist = spotify.playlist_create(user_id=social_user.uid, name=playlist.name)

        spotify_track_uris = []
        for track in playlist.tracks.all():
            if track.provider_urls.get('spotify'):
                spotify_track_uris.append(track.provider_urls.get('spotify'))
            else:
                track_sp_data = spotify.search(query=f'artist:{track.artist} track:{track.title}', types=('track', ))
                try:
                    track_sp_uri = track_sp_data[0].items[0].uri

                    track.provider_urls['spotify'] = track_sp_uri
                    track.save()
                    spotify_track_uris.append(track_sp_uri)
                except IndexError:
                    logger.info('could not find track in Spotify', extra={'artist': track.artist, 'title': track.title,
                                                                          'track_id': track.id,
                                                                          'playlist_id': playlist.id})

        spotify.playlist_add(playlist_id=spotify_playlist.id, uris=spotify_track_uris)
        return True


def create_playlist_in_target(target: PlaylistTargetService, provider: TracksProvider, playlist: Playlist) -> bool:
    tracks: list = provider.get_tracks(playlist.source_username, playlist.from_date, playlist.to_date,
                                       limit=TRACKS_LIMIT_PER_PLAYLIST)

    for track in tracks:
        track_obj: Track
        track_obj, _ = Track.objects.get_or_create(artist=track[0], title=track[1])
        track_obj.playlists.add(playlist)
        track_obj.save()

    return target.create_playlist(playlist)


def create_playlist_in_target_social_pipeline(backend, user, response, *args, **kwargs):
    try:
        playlist_id = kwargs['request'].session.pop('playlist')
    except KeyError:
        logger.warning('no playlist id in session during auth pipeline')
        raise AuthException(backend, 'Missing playlist in session, please try again')

    try:
        playlist = Playlist.objects.get(id=playlist_id)
        playlist.user = user
        playlist.status = Playlist.STARTED_CREATION
        playlist.save()
    except Playlist.DoesNotExist:
        logger.warning('playlist not found during auth pipeline')
        raise AuthException(backend, 'Internal playlist was not found, please try again')

    try:
        create_playlist_in_target(target=SpotifyPlaylistTargetService(), provider=LastFMTracksProvider(),
                                  playlist=playlist)
    except PlaylistCreationException as e:
        raise AuthException(backend, e.message)
    except Exception as e:
        logger.warning(e)
        raise AuthException(backend, 'A general error occurred, please contact support')

    playlist.status = Playlist.FINISHED_CREATION
    playlist.save()
