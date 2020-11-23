from itertools import chain
import json
from sys import exit
import logging
from contextlib import contextmanager

from instaloader import Profile
from tqdm import tqdm

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


@contextmanager
def custom_smart_run(session, threaded=False):
    try:
        session.login()
        yield
    except KeyboardInterrupt:
        exit("You have exited successfully.")
    finally:
        session.end(threaded_session=threaded)


def hashtag_is_valid(tag, browser, delay=5):
    """
    Check if a given hashtag is banned by Instagram

    :param delay: Maximum time to search for information on a page
    :param browser: A Selenium Driver
    :param tag: The hashtag to check
    :return: True if the hashtag is valid, else False
    """
    try:
        url = f"https://www.instagram.com/explore/tags/{tag}/?__a=1"
        browser.get(url)
        WebDriverWait(browser, delay).until(expected_conditions.presence_of_element_located((By.ID, 'json')))
        content = browser.find_element_by_id('json').text
        parsed_json = json.loads(content)
        return parsed_json['graphql']['hashtag']['allow_following']
    except TimeoutException:
        logging.warning(
            f'Error while checking the tag #{tag}. Loading took too much time, Please check your internet connexion.')
        return True
    except KeyError:
        return False


class UserTagChecker:
    """
    Utils for hashtags checker
    """

    def __init__(self, user, insta_loader, session):
        """
        :param user: A Instagram username
        :param insta_loader: An Instance InstaLoader
        """
        self.user = user
        self.tags = set()
        self.insta_loader = insta_loader
        self.session = session

    def get_user_hashtags(self):
        """
        Defined the list of user hashtags from all user posts
        """
        self.tags = set(chain(
            *[post.caption_hashtags for post in
              Profile.from_username(self.insta_loader.context, self.user).get_posts()]))

    def get_banned_hashtags(self):
        """
        Search banned hashtags from the list of user hashtags

        :return: The list of banned hashtags
        """
        banned_tag_list = []
        with custom_smart_run(self.session):
            for tag in tqdm(self.tags):
                if not hashtag_is_valid(tag, self.session.browser):
                    banned_tag_list.append(tag)
        return banned_tag_list
