import logging
from datetime import datetime

__version__ = "2.3.6"
__copyright__ = (
    f"Copyright 2023 - {datetime.now().year} Abishnoi69 <github.com/Abishnoi69>"
)

log = logging.getLogger(__name__)

from . import patch

log.info(f"Version: {__version__}\nCopyright: {__copyright__}")

__all__ = ["patch"]
