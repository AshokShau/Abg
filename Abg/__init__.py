import logging
from datetime import datetime

__version__ = "2.3.4"
__copyright__ = (
    f"Copyright 2023 - {datetime.now().year} Abishnoi69 <github.com/Abishnoi69>"
)

LOGGER = logging.getLogger("Abg")

from . import inline, patch

LOGGER.info(f"Version: {__version__}\nCopyright: {__copyright__}")

__all__ = ["patch"]
