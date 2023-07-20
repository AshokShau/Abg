import os

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

config = Configuration(loaders=[Environment(), EnvFile(filename=f"{os.getcwd()}/.env")])


class Config:
    OWNER_ID = int(config("OWNER_ID"))
    LOGGER_ID = config("LOGGER_ID")
    DEV_USERS = [
        int(i)
        for i in config(
            "DEV_USERS",
            default="",
        ).split(" ")
    ]
