import logging as log
from datetime import datetime

__version__ = "2.2"
__copyright__ = (
    f"Copyright 2023 - {datetime.now().year} Abishnoi69 <github.com/Abishnoi69>"
)

LOGGER = log.getLogger("Abg")

from . import chat_status, inline

LOGGER.info(f"Version: {__version__}\nCopyright: {__copyright__}")
