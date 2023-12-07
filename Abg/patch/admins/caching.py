from logging import getLogger
from threading import RLock
from time import perf_counter, time
from typing import List

from cachetools import TTLCache
from hydrogram.enums import ChatMembersFilter
from hydrogram.types import CallbackQuery
from hydrogram.types.messages_and_media.message import Message

LOGGER = getLogger(__name__)


THREAD_LOCK = RLock()

# admins stay cached for 15 mins
ADMIN_CACHE = TTLCache(maxsize=512, ttl=(60 * 15), timer=perf_counter)
# Block from refreshing admin list for 5 mins
TEMP_ADMIN_CACHE_BLOCK = TTLCache(maxsize=512, ttl=(60 * 5), timer=perf_counter)


async def admin_cache_reload(m: Message or CallbackQuery, status=None) -> List[int]:
    start = time()
    with THREAD_LOCK:
        if isinstance(m, CallbackQuery):
            m = m.message
        if status is not None:
            TEMP_ADMIN_CACHE_BLOCK[m.chat.id] = status

        try:
            if TEMP_ADMIN_CACHE_BLOCK[m.chat.id] in ("autoblock", "manualblock"):
                return []
        except KeyError:
            pass

        admin_list = [
            (
                abg.user.id,
                f"@{abg.user.username}" if abg.user.username else abg.user.first_name,
                abg.privileges.is_anonymous,
            )
            async for abg in m.chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS)
            if not abg.user.is_deleted
        ]

        ADMIN_CACHE[m.chat.id] = admin_list
        LOGGER.info(
            f"ʟᴏᴀᴅᴇᴅ ᴀᴅᴍɪɴs ғᴏʀ ᴄʜᴀᴛ {m.chat.id} ɪɴ {round((time() - start), 3)}s ᴅᴜᴇ ᴛᴏ '{status}'",
        )
        TEMP_ADMIN_CACHE_BLOCK[m.chat.id] = "autoblock"

        return admin_list
