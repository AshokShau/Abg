from functools import partial, wraps
from logging import getLogger
from typing import Union

import pyrogram
from cachetools import TTLCache
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import UserNotParticipant
from pyrogram.methods import Decorators
from pyrogram.types import CallbackQuery, Message

from Abg.config import Config

from .utils import handle_error

LOGGER = getLogger(__name__)

ANON = TTLCache(maxsize=250, ttl=30)

DEV_USER = list(Config.DEV_USERS)
DEVS = list(set([int(Config.OWNER_ID)] + DEV_USER))


async def anonymous_admin_verification(
    self, CallbackQuery: pyrogram.types.CallbackQuery
):
    if int(
        f"{CallbackQuery.message.chat.id}{CallbackQuery.data.split('.')[1]}"
    ) not in set(ANON.keys()):
        try:
            await CallbackQuery.message.edit_text("ʙᴜᴛᴛᴏɴ ʜᴀs ʙᴇᴇɴ ᴇxᴘɪʀᴇᴅ.")
        except pyrogram.types.RPCError:
            with contextlib.suppress(pyrogram.types.RPCError):
                await CallbackQuery.message.delete()
        return
    cb = ANON.pop(
        int(f"{CallbackQuery.message.chat.id}{CallbackQuery.data.split('.')[1]}")
    )
    member = await CallbackQuery.message.chat.get_member(CallbackQuery.from_user.id)
    if member.status not in (
        pyrogram.enums.ChatMemberStatus.OWNER,
        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
    ):
        return await CallbackQuery.answer(
            "ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.", show_alert=True
        )
    permission = cb[2]
    if getattr(member.privileges, permission) is True:
        try:
            await CallbackQuery.message.delete()
            await cb[1](self, cb[0])
        except pyrogram.errors.exceptions.forbidden_403.ChatAdminRequired:
            return await CallbackQuery.message.edit_text(
                "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ",
            )
        except BaseException as e:
            LOGGER.error(f"Error Found in anonymous_admin_verification:{e}")
            return
    else:
        return await CallbackQuery.message.edit_text(
            f"ʏᴏᴜ ᴀʀᴇ ᴍɪssɪɴɢ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛs ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ: {permission}"
        )


def adminsOnly(
    self,
    permissions: Union[list, str] = None,
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
        permissions (str, optional): permission type to check. Defaults to None.
        is_bot (bool, optional): If bot can perform the action. Defaults to False.
        is_user (bool, optional): If user can perform the action. Defaults to False.
        is_both (bool, optional): If both user and bot can perform the action. Defaults to False.
        only_owner (bool, optional): If only owner can perform the action. Defaults to False. (It's Chat Owner)
        only_dev (bool, optional): if only dev users can perform the operation. Defaults to False.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(
            abg: Client, message: Union[CallbackQuery, Message], *args, **kwargs
        ):
            if isinstance(message, CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
                chat = message.message.chat
                user = message.message.from_user
            else:
                sender = message.reply_text
                msg = message
                chat = message.chat
                user = message.from_user

            if msg.chat.type == ChatType.PRIVATE and not (only_dev or only_owner):
                if allow_pm:
                    return await func(abg, message, *args, *kwargs)
                return await sender("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ'ᴛ ʙᴇ ᴜsᴇᴅ ɪɴ ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ.")

            if msg.chat.type == ChatType.CHANNEL and not (only_dev or only_owner):
                if allow_channel:
                    return await func(abg, message, *args, *kwargs)
                return await sender("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ'ᴛ ʙᴇ ᴜsᴇᴅ ɪɴ ᴀ ᴄʜᴀɴɴᴇʟ.")

            if not msg.from_user:
                ANON[int(f"{msg.chat.id}{msg.id}")] = (msg, func, permissions)
                keyboard = pyrogram.types.InlineKeyboardMarkup(
                    [
                        [
                            pyrogram.types.InlineKeyboardButton(
                                text="✅ ᴘʀᴏᴠᴇ ɪᴅᴇɴᴛɪᴛʏ",
                                callback_data=f"anon.{msg.id}",
                            ),
                        ]
                    ]
                )
                return await msg.reply_text(
                    "ʏᴏᴜ'ʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴠᴇ ʏᴏᴜʀ ɪᴅᴇɴᴛɪᴛʏ",
                    reply_markup=keyboard,
                )

            try:
                bot = await chat.get_member(abg.me.id)
                user = await chat.get_member(message.from_user.id)
            except UserNotParticipant:
                return await sender(
                    f"ᴜsᴇʀ: {message.from_user.id} ɴᴏᴛ ᴍᴀᴍʙᴇʀ ᴏғ ᴛʜɪs ᴄʜᴀᴛ."
                )
            except BaseException as e:
                return await handle_error(e, msg)

            if only_owner:
                if user.status == ChatMemberStatus.OWNER:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender("ᴏɴʟʏ ᴄʜᴀᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ.")

            if only_dev:
                if msg.from_user.id in DEVS:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await sender(
                        "ᴏɴʟʏ ʙᴏᴛ ᴅᴇᴠ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ.",
                    )

            if msg.from_user.id in DEVS:
                return await func(abg, message, *args, **kwargs)

            if permissions:
                if permissions == "can_promote_members":
                    no_permission = "ᴀᴅᴅ ɴᴇᴡ ᴀᴅᴍɪɴs"
                elif permissions == "can_change_info":
                    no_permission = "ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴғᴏ"
                elif permissions == "can_pin_messages":
                    no_permission = "ᴘɪɴ/ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs"
                elif permissions == "can_invite_users":
                    no_permission = "ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ"
                elif permissions == "can_restrict_members":
                    no_permission = "ʙᴀɴ/ᴜɴʙᴀɴ ᴜsᴇʀs"
                elif permissions == "can_delete_messages":
                    no_permission = "ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs"
                elif permissions == "can_manage_chat":
                    no_permission = "ᴍᴀɴᴀɢᴇ ᴄʜᴀᴛ"
                elif permissions == "can_manage_video_chats":
                    no_permission = "ᴍᴀɴᴀɢᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ"
                elif permissions == "can_post_messages":
                    no_permission = "ᴘᴏsᴛ ᴍᴇssᴀɢᴇ"
                elif permissions == "can_edit_messages":
                    no_permission = "ᴇᴅɪᴛ ᴍᴇssᴀɢᴇ"
                elif permissions == "can_manage_topics":
                    no_permission = "ᴍᴀɴᴀɢᴇ ᴛᴏᴘɪᴄs"
                elif permissions == "is_anonymous":
                    no_permission = "ʀᴇᴍᴀɪɴ ᴀɴᴏɴʏᴍᴏᴜs"
                if is_bot:
                    if bot.status != ChatMemberStatus.ADMINISTRATOR:
                        return await sender("ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

                    if getattr(bot.privileges, permissions) is True:
                        return await func(abg, message, *args, **kwargs)
                    else:
                        return await sender(
                            f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                if is_user:
                    if user.status not in [
                        ChatMemberStatus.ADMINISTRATOR,
                        ChatMemberStatus.OWNER,
                    ]:
                        return await sender(
                            "ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ."
                        )

                    if getattr(user.privileges, permissions) is True:
                        return await func(abg, message, *args, **kwargs)
                    else:
                        return await sender(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                if is_both:
                    if bot.status != ChatMemberStatus.ADMINISTRATOR:
                        return await sender("ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

                    if getattr(bot.privileges, permissions) is True:
                        pass
                    else:
                        return await sender(
                            f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )

                    if user.status not in [
                        ChatMemberStatus.ADMINISTRATOR,
                        ChatMemberStatus.OWNER,
                    ]:
                        return await sender(
                            "ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ."
                        )

                    if getattr(user.privileges, permissions) is True:
                        pass
                    else:
                        return await sender(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                    return await func(abg, message, *args, **kwargs)
                else:
                    if is_bot:
                        if bot.status == ChatMemberStatus.ADMINISTRATOR:
                            return await func(abg, message, *args, **kwargs)
                        else:
                            return await sender(
                                "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ."
                            )
                    elif is_user:
                        if user.status in [
                            ChatMemberStatus.ADMINISTRATOR,
                            ChatMemberStatus.OWNER,
                        ]:
                            return await func(abg, message, *args, **kwargs)
                        elif msg.from_user.id in DEVS:
                            return await func(abg, message, *args, **kwargs)
                        else:
                            return await sender(
                                "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ."
                            )
                    elif is_both:
                        if user.status == ChatMemberStatus.ADMINISTRATOR:
                            pass
                        else:
                            return await sender(
                                "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ."
                            )

                        if user.status in [
                            ChatMemberStatus.ADMINISTRATOR,
                            ChatMemberStatus.OWNER,
                        ]:
                            pass
                        elif msg.from_user.id in DEVS:
                            pass
                        else:
                            return await sender(
                                "ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ."
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


Decorators.adminsOnly = adminsOnly
