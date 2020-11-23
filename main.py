from tag_detector import UserTagChecker
import instaloader
import logging
import getpass
from instapy import InstaPy

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    loader = instaloader.Instaloader()

    user = input("Your Instagram Username: ")
    passwd = getpass.getpass("Password for " + user + ": ")
    session = InstaPy(username=user, password=passwd, headless_browser=True)
    loader.login(user, passwd)

    user = input("Enter the instagram username of the account to be scanned: ")
    logging.info("Start of process...")
    ihc = UserTagChecker(user, loader, session)
    logging.info(f"Searching hashtags for user {user}...")
    ihc.get_user_hashtags()
    logging.info("End of process.")
    logging.info(f"Found {len(ihc.tags)} tags.")
    banned_tags = ihc.get_banned_hashtags()
    logging.info(f"Found {len(banned_tags)} banned tag(s).")
    if len(banned_tags):
        logging.info(f"Banned hashtags are: {', '.join([f'#{tag}' for tag in banned_tags])}")


