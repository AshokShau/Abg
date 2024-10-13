from logging import getLogger
from time import perf_counter
from typing import Any

from cachetools import TTLCache
from cachetools.keys import hashkey

LOGGER = getLogger(__name__)

try:
    import pyrogram
except ImportError:
    import hydrogram as pyrogram

# Admins stay cached for 30 minutes
member_cache = TTLCache(maxsize=512, ttl=(60 * 30), timer=perf_counter)


async def get_member_with_cache(
        chat: pyrogram.types.Chat,
        user_id: int,
        force_reload: bool = False,
) -> pyrogram.types.ChatMember | None | Any:
    """
    Get a user from the cache, or fetch and cache them if they're not already cached.

    Args:
        chat (pyrogram.types.Chat): The chat to get the user from.
        user_id (int): The user ID to get.
        force_reload (bool): Whether to bypass the cache and reload the member.

    Returns:
        pyrogram.types.ChatMember | None | Any: The user, or None if they're not a participant or if an error occurred.
    """
    cache_key = hashkey(chat.id, user_id)

    # Check if the member is in the cache and not forcing a reload
    if not force_reload and cache_key in member_cache:
        return member_cache[cache_key]

    try:
        member = await chat.get_member(user_id)
    except pyrogram.errors.UserNotParticipant:
        LOGGER.warning(f"User {user_id} is not a participant in chat {chat.id}.")
        return None
    except Exception as e:
        LOGGER.warning(f"Error found in get_member_with_cache for chat {chat.id}, user {user_id}: {e}")
        return None

    # Store in cache and return
    member_cache[cache_key] = member
    return member


async def is_admin(member: pyrogram.types.ChatMember) -> bool:
    """Check if the user is an admin in the chat."""
    return member and member.status in {pyrogram.enums.ChatMemberStatus.OWNER,
                                        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR}
