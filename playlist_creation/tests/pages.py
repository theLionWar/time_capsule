import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select

from time_capsule import settings


class BasePage:
    timeout = {
        's': 1,
        'm': 3,
        'l': 6,
        'xl': 12
    }

    def __init__(self, driver):
        self.driver = driver
        self.base_url = driver.base_url

    def goto(self, url):
        # wrapper for get()
        url = self.base_url + url
        self.driver.get(url)
        return url

    def get_base_url(self):
        return self.base_url

    def get_current_url(self):
        return self.driver.current_url

    def element(self, locator):
        # wait and get a single element via css selector (eg. #id)
        return WebDriverWait(self.driver, self.timeout['l'])\
            .until(lambda x: x.find_element(*locator))

    def select_element(self, locator):
        # wait and get a single element via css selector (eg. #id)
        return Select(self.element(locator))

    def elements(self, locator):
        # wait and get multiple elements via css selector (eg. .class)
        return WebDriverWait(self.driver, self.timeout['l'])\
            .until(lambda x: x.find_elements(*locator))

    def wait_for_element(self, locator):
        return WebDriverWait(self.driver, self.timeout['l'])\
            .until(lambda x: x.find_element(*locator))

    def sleep(self, seconds=1):
        time.sleep(seconds)

    def element_exits(self, element_css):
        # test if an element exists
        try:
            self.element(element_css)
        except NoSuchElementException:
            return False
        return True

    def switch_to_new_window(self):
        # this keeps chrome from hanging when switching windows... sadness
        self.sleep(1)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

    def switch_to_first_window(self):
        windows = self.driver.window_handles
        # close current window
        self.driver.close()
        self.driver.switch_to.window(windows[0])


class HomePage(BasePage):
    url = ''
    season_select = (By.CSS_SELECTOR, 'form #id_season')
    year_select = (By.CSS_SELECTOR, 'form #id_year')
    lastfm_user_box = (By.CSS_SELECTOR, 'form #id_lastfm_username')

    spotify_user_box = (By.CSS_SELECTOR, 'form #login-username')
    spotify_password_box = (By.CSS_SELECTOR, 'form #login-password')

    new_playlist_link = (By.CSS_SELECTOR, '#new_playlist_link')
    new_playlist_headline = (By.CSS_SELECTOR, 'h1')

    def __init__(self, driver):
        super(HomePage, self).__init__(driver)

    def fill_and_submit_form(self):
        season_select = self.select_element(self.season_select)
        season_select.select_by_visible_text('Winter')

        season_select = self.select_element(self.year_select)
        season_select.select_by_visible_text('2011')

        lastfm_user_box = self.element(self.lastfm_user_box)
        lastfm_user_box.clear()
        lastfm_user_box.send_keys('thelionwarbree')

        lastfm_user_box.send_keys(Keys.ENTER)

    def spotify_login(self):
        spotify_user_box = self.element(self.spotify_user_box)
        spotify_user_box.clear()
        spotify_user_box.send_keys(settings.TEST_SPOTIFY_USERNAME)

        spotify_password_box = self.element(self.spotify_password_box)
        spotify_password_box.clear()
        spotify_password_box.send_keys(settings.TEST_SPOTIFY_PASSWORD)

        spotify_password_box.send_keys(Keys.ENTER)

    def verify_new_playlist(self):
        new_playlist_link = self.element(self.new_playlist_link)

        assert self.get_current_url() == f'{self.get_base_url()}/thank-you/'
        assert 'YOUR PLAYLIST' in self.driver.page_source
        new_playlist_link.click()

        self.switch_to_new_window()
        assert self.element(self.new_playlist_headline).text \
               == 'Time Capsule: 2011-12-01 - 2012-02-28 (thelionwarbree)'
        return True
        # this test on the CI should run separately, against a staging env
