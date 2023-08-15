from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    LOGGER = True
    OWNER_ID = int(getenv("OWNER_ID", None))
    LOGGER_ID = getenv("LOGGER_ID", None)
    TIME_ZONE = getenv("TIME_ZONE", "Asia/Kolkata")
    DEV_USERS = set(int(x) for x in getenv("DEV_USERS", "").split())
    HANDLER = getenv("HANDLER", "/ ! + . $ #").split()


DEV_USER = list(Config.DEV_USERS)
DEVS = list(set([int(Config.OWNER_ID)] + DEV_USER))
