import pytest
from social_core.exceptions import AuthException

from playlist_creation.models import Playlist, MusicProviders, TrackPlaylist, \
    Track
from playlist_creation.services import create_playlist_in_target, \
    SpotifyPlaylistTargetService, LastFMTracksProvider, \
    create_playlist_in_target_social_pipeline


class TestCreatePlaylistCreateSongs:

    @pytest.fixture(autouse=True)
    def post_request_to_create_playlist(self, auto_login_user):
        Playlist.objects.all().delete()

        self.lastfm_username = 'thelionwarbree'
        client, self.user = auto_login_user()
        client.post('/home/', data={'season': '2', 'year': '2016',
                                    'lastfm_username': self.lastfm_username})
        self.playlist = Playlist.objects.last()
        yield

    @pytest.mark.django_db
    @pytest.mark.parametrize('providers', [[LastFMTracksProvider(), ], ])
    def test_create_playlist_tracks_created(self, mocker, providers):
        mock_spotify_create_playlist = \
            mocker.patch(
                'playlist_creation.services.SpotifyPlaylistTargetService.'
                'create_playlist'
            )
        social_user = mocker.MagicMock(provider='spotify')

        self.playlist.user = self.user
        self.playlist.save()

        create_playlist_in_target(target=SpotifyPlaylistTargetService(),
                                  providers=providers, playlist=self.playlist,
                                  social_user=social_user)

        tracks_created = Track.objects.all()
        tracks_for_playlist = \
            TrackPlaylist.objects.filter(playlist=self.playlist,
                                         source_provider=MusicProviders.LASTFM)
        assert tracks_created.count() == 48
        assert tracks_for_playlist.count() == 48

        mock_spotify_create_playlist.assert_called_with(self.playlist,
                                                        social_user)

        self.playlist.user = None
        self.playlist.save()

    @pytest.mark.django_db
    @pytest.mark.parametrize('providers', [[LastFMTracksProvider(), ], ])
    def test_create_playlist_pipeline(self, mocker, providers):
        mock_create_playlist_in_target = mocker.patch(
            'playlist_creation.services.create_playlist_in_target'
        )

        backend = mocker.MagicMock()
        request = mocker.MagicMock(session={'playlist': str(self.playlist.id)})
        social_user = mocker.MagicMock(provider='spotify')

        create_playlist_in_target_social_pipeline(backend=backend,
                                                  user=self.user,
                                                  response=None,
                                                  request=request,
                                                  social=social_user)

        self.playlist.refresh_from_db()
        assert self.playlist.user == self.user
        assert self.playlist.status == Playlist.FINISHED_CREATION
        mock_create_playlist_in_target.\
            assert_called_with(target=SpotifyPlaylistTargetService(),
                               providers=providers, playlist=self.playlist,
                               social_user=social_user)
        assert request.session['playlist_url']

    @pytest.mark.django_db
    @pytest.mark.parametrize('providers', [[LastFMTracksProvider(), ], ])
    @pytest.mark.parametrize('social_auth_providers', ['google', 'facebook'])
    def test_create_playlist_pipeline_not_spotify_user(self, mocker, providers,
                                                       social_auth_providers):
        backend = mocker.MagicMock()
        request = mocker.MagicMock(session={'playlist': str(self.playlist.id)})
        social_user = mocker.MagicMock(provider=social_auth_providers)

        with pytest.raises(AuthException):
            create_playlist_in_target_social_pipeline(backend=backend,
                                                      user=self.user,
                                                      response=None,
                                                      request=request,
                                                      social=social_user)
