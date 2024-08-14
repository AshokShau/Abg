import contextlib
from functools import partial, wraps
from logging import getLogger
from typing import Union

from cachetools import TTLCache

from Abg.config import Config

LOGGER = getLogger(__name__)
ANON = TTLCache(maxsize=250, ttl=30)
DEVS = Config.DEVS

try:
    import pyrogram
    from pyrogram import errors
except ImportError:
    import hydrogram as pyrogram
    from hydrogram import errors


async def anonymous_admin_verification(
        self, callback: pyrogram.types.CallbackQuery
):
    if int(
            f"{callback.message.chat.id}{callback.data.split('.')[1]}"
    ) not in set(ANON.keys()):
        try:
            await callback.message.edit_text("Button has been expired")
        except errors.RPCError:
            with contextlib.suppress(errors.RPCError):
                await callback.message.delete()
        return
    cb = ANON.pop(
        int(f"{callback.message.chat.id}{callback.data.split('.')[1]}")
    )
    member = await callback.message.chat.get_member(callback.from_user.id)
    if member.status not in (
            pyrogram.enums.ChatMemberStatus.OWNER,
            pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
    ):
        return await callback.answer(
            "You need to be an admin to do this", show_alert=True
        )
    permission = cb[2]
    if getattr(member.privileges, permission) is True:
        try:
            await callback.message.delete()
            await cb[1](self, cb[0])
        except pyrogram.errors.exceptions.forbidden_403.ChatAdminRequired:
            return await callback.message.edit_text(
                "I must be an admin to execute this command",
            )
        except BaseException as e:
            LOGGER.error(f"Error Found in anonymous_admin_verification:{e}")
            return await callback.message.edit_text("An error occurred.")
    else:
        return await callback.message.edit_text(f"You don't have permission to {permission}.")


def adminsOnly(
        self,
        permissions: Union[str] = None,
        is_bot: bool = False,
        is_user: bool = False,
        is_both: bool = False,
        only_owner: bool = False,
        only_dev: bool = False,
        allow_pm: bool = True,
        allow_channel: bool = True,
):
    """Check for permission level to perform some operations

    Args:
        self:
        permissions (str, optional): permission type to check. Defaults to None.
        is_bot (bool, optional): If bot can perform the action. Defaults to False.
        is_user (bool, optional): If user can perform the action. Defaults to False.
        is_both (bool, optional): If both user and bot can perform the action. Defaults to False.
        only_owner (bool, optional): If only owner can perform the action. Defaults to False. (It's Chat Owner)
        only_dev (bool, optional): if only dev users can perform the operation. Defaults to False.
        allow_channel (bool, optional): If the command can be used in channels. Defaults to True.
        allow_pm (bool, optional): If the command can be used in PM. Defaults to True.
    """

    def decorator(func):
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
                    return await func(abg, message, *args, *kwargs)
                return await sender("This command can't be used in PM.")

            if msg.chat.type == pyrogram.enums.ChatType.CHANNEL and not (only_dev or only_owner):
                if allow_channel:
                    return await func(abg, message, *args, *kwargs)
                return await sender("This command can't be used in channels.")

            if not msg.from_user:
                ANON[int(f"{msg.chat.id}{msg.id}")] = (msg, func, permissions)
                keyboard = pyrogram.types.InlineKeyboardMarkup(
                    [
                        [
                            pyrogram.types.InlineKeyboardButton(
                                text="✅ Verify Admin",
                                callback_data=f"anon.{msg.id}",
                            ),
                        ]
                    ]
                )
                return await msg.reply_text(
                    "Please verify that you are an admin to perform this action.",
                    reply_markup=keyboard,
                )

            try:
                bot = await chat.get_member(abg.me.id)
                user = await chat.get_member(message.from_user.id)
            except pyrogram.errors.exceptions.bad_request_400.ChatAdminRequired:
                return await sender(f"I must be admin to execute this command.")
            except pyrogram.errors.exceptions.forbidden_403.ChatAdminRequired:
                return await sender(f"I must be admin to execute this command.")
            except errors.UserNotParticipant:
                return await sender(
                    f"User: {message.from_user.first_name} not member of this chat."
                )
            except Exception as e:
                LOGGER.error(f"Error Found in adminsOnly:{e}")
                return await sender(f"An error occurred: {e}")

            if only_dev:
                if msg.from_user.id in DEVS:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender(
                        "Only devs can perform this action.",
                    )

            if msg.from_user.id in DEVS:
                return await func(abg, message, *args, **kwargs)

            if only_owner:
                if user.status == pyrogram.enums.ChatMemberStatus.OWNER:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender("Only chat owner can perform this action")

            if permissions:
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
                anonymous_admin_verification,
                pyrogram.filters.regex("^anon."),
            ),
        )
        return wrapper

    return decorator


pyrogram.methods.Decorators.adminsOnly = adminsOnly
