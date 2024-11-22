import contextlib
from functools import partial, wraps
from logging import getLogger
from typing import Union, Callable, Any, Optional

from cachetools import TTLCache

from Abg.config import Config
from .cache import is_admin, is_owner, get_admin_cache_user, load_admin_cache

LOGGER = getLogger(__name__)
ANON = TTLCache(maxsize=250, ttl=30)
DEVS = Config.DEVS

try:
    import pyrogram
    from pyrogram import errors
except ImportError:
    import hydrogram as pyrogram
    from hydrogram import errors



def ensure_permissions_list(permissions: Union[str, list[str]]) -> list[str]:
    """
    Ensures permissions are a list of strings.
    """
    return [permissions] if isinstance(permissions, str) else permissions or []


async def check_permissions(chat_id: int, user_id: int, permissions: Union[str, list[str]]) -> bool:
    """
    Check if a user has specific permissions.
    """

    tg_admin = 777000
    anonymous_admin = 1087968824
    if user_id in [tg_admin, anonymous_admin]:
        return True

    if not await is_admin(chat_id, user_id):
        return False

    if await is_owner(chat_id, user_id):
        return True

    permissions = ensure_permissions_list(permissions)
    if not permissions:
        return True

    _, user_info = await get_admin_cache_user(chat_id, user_id)
    if not user_info:
        return False

    return all(getattr(user_info.privileges, perm, False) for perm in permissions)



async def verify_anonymous_admin(
        self, callback: pyrogram.types.CallbackQuery
) -> None:
    """Verify anonymous admin permissions."""
    callback_id = int(f"{callback.message.chat.id}{callback.data.split('.')[1]}")
    if callback_id not in ANON:
        try:
            await callback.message.edit_text("Button has been expired")
        except (errors.RPCError, AttributeError):
            with contextlib.suppress(errors.RPCError):
                await callback.message.delete()
        return

    message, func, permissions = ANON.pop(callback_id)
    if not message:
        await callback.answer("Failed to get message", show_alert=True)
        return

    if not await check_permissions(message.chat.id, callback.from_user.id, permissions):
        await callback.answer(f"You don't have the required permissions: {', '.join(ensure_permissions_list(permissions))}" , show_alert=True)
        return

    try:
        await callback.message.delete()
        await func(self, message)
    except pyrogram.errors.exceptions.forbidden_403.ChatAdminRequired:
        await callback.message.edit_text("I must be an admin to execute this command")
    except BaseException as e:
        LOGGER.error(f"Error in verify_anonymous_admin: {e}")


def adminsOnly(
        self: pyrogram.Client,
        permissions: Optional[Union[str, list[str]]] = None,
        is_bot: bool = False,
        is_user: bool = False,
        is_both: bool = False,
        only_owner: bool = False,
        only_dev: bool = False,
        allow_pm: bool = True,
        allow_channel: bool = True,
        no_reply: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to check if the user is an admin in the chat before executing the command.

    Args:
        self: The client instance.
        permissions: List of permissions that the user must have to execute the command.
        is_bot: If True, the bot must have the specified permissions in the chat.
        is_user: If True, the user must have the specified permissions in the chat.
        is_both: If True, the bot and user must have the specified permissions in the chat.
        only_owner: If True, only the chat owner can execute the command.
        only_dev: If True, only the devs can execute the command.
        allow_pm: If False, the command can't be used in PM.
        allow_channel: If False, the command can't be used in channels.
        no_reply: If True, the command will not reply to the user if the user is not an admin.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(
                abg: pyrogram.Client, message: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message], *args,
                **kwargs
        ):
            """
            Check if the user is an admin in the chat before executing the command.
            """
            # If message is None, return
            if message is None:
                return

            # If message is a CallbackQuery, get the message and chat
            if isinstance(message, pyrogram.types.CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
                chat = message.message.chat
            else:
                # If message is a Message, get the message and chat
                sender = message.reply_text
                msg = message
                chat = message.chat

            # If chat is None, return
            if chat is None:
                return await sender("Chat is None.")

            # If the message is from an anonymous admin, store the message and the function in the ANON dictionary
            if not msg.from_user and not no_reply:
                ANON[int(f"{msg.chat.id}{msg.id}")] = (msg, func, permissions)
                keyboard = pyrogram.types.InlineKeyboardMarkup(
                    [
                        [
                            pyrogram.types.InlineKeyboardButton(
                                text="Verify Admin",
                                callback_data=f"anon.{msg.id}",
                            ),
                        ]
                    ]
                )
                return await msg.reply_text(
                    "Please verify that you are an admin to perform this action.",
                    reply_markup=keyboard,
                )

            user_id = message.from_user.id
            chat_id = chat.id
            if only_dev and user_id not in Config.DEVS:
                if no_reply:
                    return None
                return await sender("Only developers can use this command.")

            if not allow_pm and chat.type == pyrogram.enums.ChatType.PRIVATE:
                if no_reply:
                    return None
                return await sender("This command can only be used in groups.")

            if not allow_channel and chat.type == pyrogram.enums.ChatType.CHANNEL:
                if no_reply:
                    return None
                return await sender("This command can only be used in groups or private chats.")

            load, _ = await load_admin_cache(abg, chat_id)
            if not load:
                if no_reply:
                    return None
                return await sender("I need to be an admin to do this.")

            if only_owner and not await is_owner(chat_id, user_id):
                if no_reply:
                    return None
                return await sender("Only the chat owner can use this command.")

            async def check_and_notify(subject_id, subject_name) -> Optional[bool]:
                if not await is_admin(chat_id, subject_id):
                    if no_reply:
                        return None
                    await sender(f"{subject_name} needs to be an admin.")
                    return False

                if not await check_permissions(chat_id, subject_id, permissions):
                    if no_reply:
                        return None
                    await sender(f"{subject_name} lacks required permissions: {', '.join(ensure_permissions_list(permissions))}.")
                    return False
                return True

            if is_bot and not await check_and_notify(abg.me.id, "I"):
                return None
            if is_user and not await check_and_notify(user_id, "You"):
                return None
            if is_both and (not await check_and_notify(user_id, "You") or not await check_and_notify(abg.me.id, "I")):
                return None
            return await func(abg, message, *args, **kwargs)

        self.add_handler(
            pyrogram.handlers.CallbackQueryHandler(
                verify_anonymous_admin,
                pyrogram.filters.regex("^anon."),
            ),
        )
        return wrapper

    return decorator


pyrogram.methods.Decorators.adminsOnly = adminsOnly
