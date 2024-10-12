from logging import getLogger
from time import perf_counter
from cachetools import TTLCache
from cachetools.keys import hashkey

LOGGER = getLogger(__name__)

try:
    import pyrogram
except ImportError:
    import hydrogram as pyrogram

# Admins stay cached for 30 minutes
member_cache = TTLCache(maxsize=512, ttl=(60 * 30), timer=perf_counter)


async def get_member_with_cache(chat: pyrogram.types.chat, user_id):
    cache_key = hashkey(chat.id, user_id)

    # Check if the member is in the cache
    if cache_key in member_cache:
        print("from cache")
        return member_cache[cache_key]

    try:
        member = await chat.get_member(user_id)
    except pyrogram.errors.UserNotParticipant:
        LOGGER.warning(f"User {user_id} is not a participant in chat {chat.id}.")
        return None
    except Exception as e:
        LOGGER.warning(f"Error found in get_member_with_cache for chat {chat.id}, user {user_id}: {e}")
        return None
    print("from non cache")
    # Store in cache and return
    member_cache[cache_key] = member
    return member
