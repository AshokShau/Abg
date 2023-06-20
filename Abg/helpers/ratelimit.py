from functools import wraps
from typing import Callable, Union

from cachetools import TTLCache
from pyrate_limiter import (
    BucketFullException,
    Duration,
    Limiter,
    MemoryListBucket,
    RequestRate,
)
from pyrogram import Client
from pyrogram.errors import QueryIdInvalid
from pyrogram.types import CallbackQuery, Message

# you need to install this using : pip3 install pyrate_limiter


class RateLimiter:
    """
    Implement rate limit logic using leaky bucket
    algorithm, via pyrate_limiter.
    (https://pypi.org/project/pyrate-limiter/)
    """

    def __init__(self) -> None:
        # 2 requests per seconds
        self.second_rate = RequestRate(2, Duration.SECOND)

        # 15 requests per minute.
        self.minute_rate = RequestRate(15, Duration.MINUTE)

        # 500 requests per hour
        self.hourly_rate = RequestRate(500, Duration.HOUR)

        # 1500 requests per day
        self.daily_rate = RequestRate(1500, Duration.DAY)

        self.limiter = Limiter(
            self.minute_rate,
            self.hourly_rate,
            self.daily_rate,
            bucket_class=MemoryListBucket,
        )

    async def acquire(self, userid: Union[int, str]) -> bool:
        """
        Acquire rate limit per userid and return True / False
        based on userid ratelimit status.
        """

        try:
            self.limiter.try_acquire(userid)
            return False
        except BucketFullException:
            return True


ratelimit = RateLimiter()

warned_users = TTLCache(maxsize=128, ttl=60)

warning_message = "sᴘᴀᴍ ᴅᴇᴛᴇᴄᴛᴇᴅ! ɪɢɴᴏʀɪɴɢ ʏᴏᴜʀ ᴀʟʟ ʀᴇǫᴜᴇsᴛs ғᴏʀ ғᴇᴡ ᴍɪɴᴜᴛᴇs."


def ratelimiter(func: Callable) -> Callable:
    """
    Restricts user's from spamming commands or pressing buttons multiple times
    using leaky bucket algorithm and pyrate_limiter.
    """

    @wraps(func)
    async def decorator(client: Client, update: Union[Message, CallbackQuery]):
        userid = update.from_user.id if update.from_user else update.sender_chat.id
        is_limited = await ratelimit.acquire(userid)

        if is_limited and userid not in warned_users:
            if isinstance(update, Message):
                await update.reply_text(warning_message)
                warned_users[userid] = 1
                return

            elif isinstance(update, CallbackQuery):
                try:
                    await update.answer(warning_message, show_alert=True)
                except QueryIdInvalid:
                    warned_users[userid] = 1
                    return
                warned_users[userid] = 1
                return

        elif is_limited and userid in warned_users:
            pass
        else:
            return await func(client, update)

    return decorator
