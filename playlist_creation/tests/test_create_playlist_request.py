import pytest
from django.contrib.sessions.backends.db import SessionStore
from playlist_creation.models import Playlist, MusicProviders


class TestCreatePlaylistFlow:

    @pytest.fixture(autouse=True)
    def post_request_to_create_playlist(self, auto_login_user):
        self.lastfm_username = 'thelionwarbree'
        client, user = auto_login_user()
        self.response_post = client.post('/home/', data={'season': '2', 'year': '2018',
                                                         'lastfm_username': self.lastfm_username})
        yield

    @pytest.mark.django_db
    def test_create_playlist_redirected_to_spotify_login_flow(self):
        assert self.response_post.status_code == 302
        assert self.response_post.url == '/login/spotify/'

    @pytest.mark.django_db
    def test_create_playlist_playlist_created(self):
        assert Playlist.objects.count() == 1
        playlist = Playlist.objects.last()
        assert playlist.source_providers == {MusicProviders.LASTFM: self.lastfm_username}

    @pytest.mark.django_db
    def test_create_playlist_playlist_added_to_session(self):
        playlist = Playlist.objects.last()
        session_key = self.response_post.cookies['sessionid'].value
        s = SessionStore(session_key=session_key)
        assert s['playlist'] == str(playlist.id)
