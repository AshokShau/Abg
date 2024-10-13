import logging
from datetime import datetime

from .__version__ import __version__

__copyright__ = (
    f"Copyright 2023 - {datetime.now().year} AshokShau <github.com/AshokShau>"
)

log = logging.getLogger(__name__)
log.info(f"Version: {__version__}\nCopyright: {__copyright__}")

from .patch import *  # types :ignore
