import contextlib
from functools import partial, wraps
from logging import getLogger
from typing import Union, Callable, Any, Optional, List

from cachetools import TTLCache

from Abg.config import Config
from Abg.patch.decorators.cache import get_member_with_cache

LOGGER = getLogger(__name__)
ANON = TTLCache(maxsize=250, ttl=30)
DEVS = Config.DEVS

try:
    import pyrogram
    from pyrogram import errors
except ImportError:
    import hydrogram as pyrogram
    from hydrogram import errors

# Permission error messages mapping
PERMISSION_ERROR_MESSAGES = {
    "can_delete_messages": "delete messages",
    "can_change_info": "change chat info",
    "can_promote_members": "promote members",
    "can_pin_messages": "pin messages",
    "can_invite_users": "invite users",
    "can_restrict_members": "restrict members",
    "can_manage_chat": "manage chat",
    "can_post_messages": "post messages",
    "can_edit_messages": "edit messages",
    "can_manage_video_chats": "manage video chats",
    "can_send_messages": "send messages",
    "can_send_media_messages": "send media messages",
    "can_send_other_messages": "send other types of messages",
    "can_send_polls": "send polls",
    "can_add_web_page_previews": "add web page previews",
    "can_manage_topics": "manage topics",
}


async def verify_anonymous_admin(
        self, callback: pyrogram.types.CallbackQuery
) -> None:
    """Verify anonymous admin permissions."""
    callback_id = int(f"{callback.message.chat.id}{callback.data.split('.')[1]}")
    if callback_id not in ANON:
        try:
            await callback.message.edit_text("Button has been expired")
        except errors.RPCError:
            with contextlib.suppress(errors.RPCError):
                await callback.message.delete()
        return

    message, func, permission = ANON.pop(callback_id)
    member = await get_member_with_cache(callback.message.chat, callback.from_user.id)

    if member is None:
        await callback.answer("Failed to get member's status", show_alert=True)
        return

    if member.status not in (
            pyrogram.enums.ChatMemberStatus.OWNER,
            pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
    ):
        await callback.answer("You need to be an admin to do this", show_alert=True)
        return

    if isinstance(permission, str):
        if getattr(member.privileges, permission) is not True:
            await callback.message.edit_text(f"You don't have permission to {PERMISSION_ERROR_MESSAGES.get(permission, permission)}.")
            return
    elif isinstance(permission, list):
        for perm in permission:
            if getattr(member.privileges, perm) is not True:
                await callback.message.edit_text(f"You don't have permission to {PERMISSION_ERROR_MESSAGES.get(perm, perm)}.")
                return
    else:
        raise ValueError(f"Invalid permission type: {type(permission)}")

    try:
        await callback.message.delete()
        await func(self, message)
    except pyrogram.errors.exceptions.forbidden_403.ChatAdminRequired:
        await callback.message.edit_text("I must be an admin to execute this command")
    except BaseException as e:
        LOGGER.error(f"Error in verify_anonymous_admin: {e}")


def adminsOnly(
        self: pyrogram.Client,
        permissions: Optional[Union[str, List[str]]] = None,
        is_bot: bool = False,
        is_user: bool = False,
        is_both: bool = False,
        only_owner: bool = False,
        only_dev: bool = False,
        allow_pm: bool = True,
        allow_channel: bool = True,
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
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(
                abg: pyrogram.Client, message: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message], *args,
                **kwargs
        ):
            if isinstance(message, pyrogram.types.CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
                chat = message.message.chat
            else:
                sender = message.reply_text
                msg = message
                chat = message.chat

            if msg.chat.type == pyrogram.enums.ChatType.PRIVATE and not (only_dev or only_owner):
                if allow_pm:
                    return await func(abg, message, *args, **kwargs)
                return await sender("This command can't be used in PM.")

            if msg.chat.type == pyrogram.enums.ChatType.CHANNEL and not (only_dev or only_owner):
                if allow_channel:
                    return await func(abg, message, *args, **kwargs)
                return await sender("This command can't be used in channels.")

            if not msg.from_user:
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

            bot = await get_member_with_cache(chat, abg.me.id)
            user = await get_member_with_cache(chat, message.from_user.id)

            if bot is None or user is None:
                return sender("Could not retrieve member information.")

            if only_dev:
                if msg.from_user.id in DEVS:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender("Only devs can perform this action.")

            if msg.from_user.id in DEVS:
                return await func(abg, message, *args, **kwargs)

            if only_owner:
                if user.status == pyrogram.enums.ChatMemberStatus.OWNER:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender("Only chat owner can perform this action")

            missing_permissions = []

            def check_permissions(member_privileges, permissions_list):
                for permission in (permissions if isinstance(permissions, list) else [permissions]):
                    if getattr(member_privileges, permission) is not True:
                        missing_permissions.append(permission)

            if is_bot:
                if bot.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
                    return await sender("I must be admin to execute this command.")
                check_permissions(bot.privileges, permissions)

                if missing_permissions:
                    return await sender(f"I don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

            if is_user:
                if user.status not in [
                    pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                    pyrogram.enums.ChatMemberStatus.OWNER,
                ]:
                    return await sender("You must be an admin to use this command.")
                check_permissions(user.privileges, permissions)

                if missing_permissions:
                    return await sender(f"You don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

            if is_both:
                if bot.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
                    return await sender("I must be admin to execute this command.")
                check_permissions(bot.privileges, permissions)

                if missing_permissions:
                    return await sender(f"I don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

                missing_permissions.clear()  # Clear for user check
                if user.status not in [
                    pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                    pyrogram.enums.ChatMemberStatus.OWNER,
                ]:
                    return await sender("You must be an admin to use this command.")
                check_permissions(user.privileges, permissions)

                if missing_permissions:
                    return await sender(f"You don't have permission to {', '.join(PERMISSION_ERROR_MESSAGES.get(p, p) for p in missing_permissions)}.")

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
