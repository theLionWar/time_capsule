import uuid
import pytest


@pytest.fixture
def test_password():
    return 'strong-test-pass'


@pytest.fixture
def test_with_specific_settings(settings):
    settings.BASICAUTH_DISABLE = True


@pytest.fixture
def create_user(db, django_user_model, test_password,
                test_with_specific_settings):
    def make_user(**kwargs):
        kwargs['password'] = test_password
        if 'username' not in kwargs:
            kwargs['username'] = str(uuid.uuid4())
        return django_user_model.objects.create_user(**kwargs)
    return make_user


@pytest.fixture
def auto_login_user(db, client, create_user, test_password,
                    test_with_specific_settings):
    def make_auto_login(user=None):
        if user is None:
            user = create_user()
            client.login(username=user.username, password=test_password)
        return client, user
    return make_auto_login
