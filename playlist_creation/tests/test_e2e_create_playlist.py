import pytest

from playlist_creation.tests.pages import HomePage


@pytest.fixture(scope="module", autouse=True)
def setup(driver):
    # makes pages available to all tests
    global homePage
    homePage = HomePage(driver)
    homePage.goto(homePage.url)


@pytest.mark.skip(reason='in order to run e2e - '
                         'run a local server on 8000 port, '
                         'and comment out this decorator. '
                         'Instruction to upgrade chromedriver '
                         'in useful tips file')
def test_create_playlist(driver, db):
    homePage.fill_and_submit_form()
    homePage.spotify_login()
    assert homePage.verify_new_playlist()
