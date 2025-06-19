import os

from dotenv import load_dotenv


load_dotenv()


IGNORED_USERS = ['Animingle']
ACCEPTABLE_BANGS = ['!an', '!am', '!animingle']
ACCEPTABLE_COMMANDS = ['recent', 'help', 'all', 'summary']


HEADERS = {
    'X-MAL-CLIENT-ID': os.getenv('CLIENT_ID')
}
