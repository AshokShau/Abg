from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    HANDLER = getenv("HANDLER", "/ ! + . $ #").split()
    devs_env = getenv("DEVS")
    DEVS = list(map(int, devs_env.split())) if devs_env else []
