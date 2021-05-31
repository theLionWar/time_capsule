
class TestCreatePlaylistFlow:

    def test_redirect_to_home(self, client, test_with_specific_settings):
        self.response_get = client.get('/')
        assert self.response_get.status_code == 302
        assert self.response_get.url == '/home/'
