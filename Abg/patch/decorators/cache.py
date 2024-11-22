from logging import getLogger
from typing import Optional, Tuple
from cachetools import TTLCache


LOGGER = getLogger(__name__)

try:
    import pyrogram
except ImportError:
    import hydrogram as pyrogram

# Initialize TTLCache with a max size and TTL (Time-to-live)
admin_cache = TTLCache(maxsize=1000, ttl=15 * 60)  # 16 minutes TTL


class AdminCache:
    def __init__(self, chat_id: int, user_info: list[pyrogram.types.ChatMember], cached: bool = True):
        self.chat_id = chat_id
        self.user_info = user_info
        self.cached = cached

    def get_user_info(self, user_id: int) -> Optional[pyrogram.types.ChatMember]:
        return next((user for user in self.user_info if user.user.id == user_id), None)


async def load_admin_cache(client: pyrogram.Client, chat_id: int, force_reload: bool = False) -> Tuple[bool, AdminCache]:
    """
    Load the admin list from Telegram and cache it, unless already cached.
    Set force_reload to True to bypass the cache and reload the admin list.
    """
    # Check if the cache is already populated for the chat_id
    if not force_reload and chat_id in admin_cache:
        return True, admin_cache[chat_id]  # Return the cached data if available and reload not forced

    try:
        # Retrieve and cache the admin list
        admin_list = []
        async for m in client.get_chat_members(chat_id, filter=pyrogram.enums.ChatMembersFilter.ADMINISTRATORS):
            # Filter out deleted users
            if m.user.is_deleted:
                continue
            admin_list.append(m)

        admin_cache[chat_id] = AdminCache(chat_id, admin_list)
        return True, admin_cache[chat_id]
    except Exception as e:
        LOGGER.error(f"Error loading admin cache for chat_id {chat_id}: {e}")
        # Return an empty AdminCache with `cached=False` if there was an error
        return False, AdminCache(chat_id, [], cached=False)


async def get_admin_cache_user(chat_id: int, user_id: int) -> Tuple[bool, Optional[pyrogram.types.ChatMember]]:
    """
    Check if the user is an admin using cached data.
    """
    admin_list = admin_cache.get(chat_id)
    if admin_list is None:
        return False, None  # Cache miss; admin list not available

    return next(
        (
            (True, user_info)
            for user_info in admin_list.user_info
            if user_info.user.id == user_id
        ),
        (False, None),
    )


async def is_owner(chat_id: int, user_id: int) -> bool:
    """
    Check if the user is the owner of the chat.
    """
    is_cached, user_info = await get_admin_cache_user(chat_id, user_id)
    return bool(
        is_cached and user_info.status == pyrogram.enums.ChatMemberStatus.OWNER
    )



async def is_admin(chat_id: int, user_id: int) -> bool:
    """
    Check if the user is an admin (including the owner) in the chat.
    """
    is_cached, user_info = await get_admin_cache_user(chat_id, user_id)
    return bool(
        is_cached
        and user_info.status
        in [
            pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
            pyrogram.enums.ChatMemberStatus.OWNER,
        ]
    )
