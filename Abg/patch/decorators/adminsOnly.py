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


async def verify_anonymous_admin(
        self, callback: pyrogram.types.CallbackQuery
) -> None:
    """Verify anonymous admin permissions."""
    # Get the callback data from the cache
    callback_id = int(f"{callback.message.chat.id}{callback.data.split('.')[1]}")
    if callback_id not in ANON:
        # Button has been expired
        try:
            await callback.message.edit_text("Button has been expired")
        except errors.RPCError:
            # Ignore if the message can't be edited/deleted
            with contextlib.suppress(errors.RPCError):
                await callback.message.delete()
        return

    # Get the callback data from the cache
    message, func, permission = ANON.pop(callback_id)

    # Get the member's status
    member = await get_member_with_cache(callback.message.chat, callback.from_user.id)
    if member is None:
        await callback.answer("Failed to get member's status", show_alert=True)
        return

    # Check if the member is an admin
    if member.status not in (
            pyrogram.enums.ChatMemberStatus.OWNER,
            pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
    ):
        await callback.answer(
            "You need to be an admin to do this", show_alert=True
        )
        return

    # Check if the member has the required permission
    if getattr(member.privileges, permission) is not True:
        await callback.message.edit_text(
            f"You don't have permission to {permission}."
        )
        return

    # Execute the callback function
    try:
        await callback.message.delete()
        await func(self, message)
    except pyrogram.errors.exceptions.forbidden_403.ChatAdminRequired:
        await callback.message.edit_text(
            "I must be an admin to execute this command",
        )
    except BaseException as e:
        LOGGER.error(f"Error in verify_anonymous_admin: {e}")


def adminsOnly(
        self,
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
        self: The Client object.
        permissions: The permission required to execute the command. If None, the user must be an admin.
        is_bot: If True, the bot must be an admin.
        is_user: If True, the user must be an admin.
        is_both: If True, both the bot and the user must be an admin.
        only_owner: If True, only the owner of the chat can execute the command.
        only_dev: If True, only devs can execute the command.
        allow_pm: If True, the command can be used in PM.
        allow_channel: If True, the command can be used in channels.

    Returns:
        A decorator that checks if the user is an admin in the chat before executing the command.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator to check if the user is an admin in the chat before executing the command.

        Args:
            func: The function to decorate.

        Returns:
            The decorated function.
        """
        @wraps(func)
        async def wrapper(
                abg: pyrogram.Client, message: Union[pyrogram.types.CallbackQuery, pyrogram.types.Message], *args,
                **kwargs
        ):
            """
            Check if the user is an admin in the chat before executing the command.

            If the user is an admin, execute the command.
            If the user is not an admin, return a message saying that they don't have permission.
            """
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
                    return await func(abg, message, *args, *kwargs)
                return await sender("This command can't be used in PM.")

            if msg.chat.type == pyrogram.enums.ChatType.CHANNEL and not (only_dev or only_owner):
                if allow_channel:
                    return await func(abg, message, *args, *kwargs)
                return await sender("This command can't be used in channels.")

            if not msg.from_user:
                # If the message is from an anonymous user, ask them to verify that they are an admin.
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
                # If the user is not a dev, return a message saying that they don't have permission.
                if msg.from_user.id in DEVS:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender(
                        "Only devs can perform this action.",
                    )

            if msg.from_user.id in DEVS:
                return await func(abg, message, *args, **kwargs)

            if only_owner:
                # If the user is not the owner of the chat, return a message saying that they don't have permission.
                if user.status == pyrogram.enums.ChatMemberStatus.OWNER:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender("Only chat owner can perform this action")

            if permissions:
                # If the user doesn't have the required permission, return a message saying that they don't have permission.
                no_permission = permissions
                if permissions == "can_promote_members":
                    no_permission = "promote members"
                elif permissions == "can_change_info":
                    no_permission = "change chat info"
                elif permissions == "can_pin_messages":
                    no_permission = "pin messages"
                elif permissions == "can_invite_users":
                    no_permission = "invite users"
                elif permissions == "can_restrict_members":
                    no_permission = "restrict members"
                elif permissions == "can_delete_messages":
                    no_permission = "delete messages"
                elif permissions == "can_manage_chat":
                    no_permission = "manage chat"
                elif permissions == "can_manage_video_chats":
                    no_permission = "manage video chats"
                elif permissions == "can_post_messages":
                    no_permission = "post messages"
                elif permissions == "can_edit_messages":
                    no_permission = "edit messages"
                elif permissions == "can_manage_topics":
                    no_permission = "manage chat topics"
                elif permissions == "is_anonymous":
                    no_permission = "anonymous"
                if is_bot:
                    if bot.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
                        return await sender("I must be admin to execute this command.")

                    if getattr(bot.privileges, permissions) is True:
                        return await func(abg, message, *args, **kwargs)
                    else:
                        return await sender(
                            f"I don't have permission to {no_permission}."
                        )
                if is_user:
                    if user.status not in [
                        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                        pyrogram.enums.ChatMemberStatus.OWNER,
                    ]:
                        return await sender(
                            "You must be an admin to use this command."
                        )

                    if getattr(user.privileges, permissions) is True:
                        return await func(abg, message, *args, **kwargs)
                    else:
                        return await sender(
                            f"You don't have permission to {no_permission}."
                        )
                if is_both:
                    if bot.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
                        return await sender("I must be admin to execute this command.")

                    if getattr(bot.privileges, permissions) is True:
                        pass
                    else:
                        return await sender(
                            f"I don't have permission to {no_permission}."
                        )

                    if user.status not in [
                        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                        pyrogram.enums.ChatMemberStatus.OWNER,
                    ]:
                        return await sender(
                            "You must be an admin to use this command."
                        )

                    if getattr(user.privileges, permissions) is True:
                        pass
                    else:
                        return await sender(
                            f"You don't have permission to {no_permission}."
                        )
                    return await func(abg, message, *args, **kwargs)
                else:
                    if is_bot:
                        if bot.status == pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
                            return await func(abg, message, *args, **kwargs)
                        else:
                            return await sender(
                                "I must be admin to execute this command."
                            )
                    elif is_user:
                        if user.status in [
                            pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                            pyrogram.enums.ChatMemberStatus.OWNER,
                        ]:
                            return await func(abg, message, *args, **kwargs)
                        elif msg.from_user.id in DEVS:
                            return await func(abg, message, *args, **kwargs)
                        else:
                            return await sender(
                                "You must be an admin to use this command."
                            )
                    elif is_both:
                        if bot.status == pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
                            pass
                        else:
                            return await sender(
                                "I must be admin to execute this command."
                            )

                        if user.status in [
                            pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                            pyrogram.enums.ChatMemberStatus.OWNER,
                        ]:
                            pass
                        elif msg.from_user.id in DEVS:
                            pass
                        else:
                            return await sender(
                                "You must be an admin to use this command"
                            )
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
