import typing
from functools import wraps
from logging import getLogger
from typing import Union

import pyrogram
from cachetools import TTLCache
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.methods import Decorators
from pyrogram.types import CallbackQuery, ChatPrivileges, Message

from config import Config

LOGGER = getLogger(__name__)

ANON = TTLCache(maxsize=250, ttl=30)


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
    no_reply: object = False,
    pass_anon: typing.Union[bool, bool] = False,
):
    """Check for permission level to perform some operations

    Args:
        permissions (str, optional): permission type to check. Defaults to None.
        is_bot (bool, optional): If bot can perform the action. Defaults to False.
        is_user (bool, optional): If user can perform the action. Defaults to False.
        is_both (bool, optional): If both user and bot can perform the action. Defaults to False.
        only_owner (bool, optional): If only owner can perform the action. Defaults to False.
        no_reply (boot, optional): If should not reply. Defaults to False.
        pass_anon (boot, optional): If the user is an Anonymous Admin, then it bypasses his right check.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(
            abg: Client, message: Union[CallbackQuery, Message], *args, **kwargs
        ):
            if isinstance(message, CallbackQuery):
                msg = message.message
            elif isinstance(message, Message):
                msg = message
                is_anon = message.sender_chat
            else:
                raise NotImplementedError(
                    f"require_admin can't process updates with the type '{message.__name__}' yet."
                )
            chat = msg.chat
            user = msg.from_user

            if msg.chat.type == ChatType.PRIVATE and not (only_dev or only_owner):
                return await func(abg, message, *args, *kwargs)

            if msg.chat.type == ChatType.CHANNEL:
                return await func(abg, message, *args, *kwargs)

            if not message.from_user and not pass_anon:
                ANON[int(f"{msg.chat.id}{msg.id}")] = (
                    message,
                    func,
                    permissions,
                )
                keyboard = pyrogram.types.InlineKeyboardMarkup(
                    [
                        [
                            pyrogram.types.InlineKeyboardButton(
                                text="ᴘʀᴏᴠᴇ ɪᴅᴇɴᴛɪᴛʏ ",
                                callback_data=f"anon.{msg.id}",
                            ),
                        ]
                    ]
                )
                return await msg.reply_text(
                    "ʏᴏᴜ'ʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴠᴇ ʏᴏᴜʀ ɪᴅᴇɴᴛɪᴛʏ",
                    reply_markup=keyboard,
                )

            bot = (
                await abg.get_chat_member(chat.id, abg.me.id)
                if is_bot or is_both
                else None
            )
            user = (
                await abg.get_chat_member(chat.id, user.id)
                if is_user or is_both
                else None
            )
            # looks like todo for now (when pyrogram support `ChatMemberOwner`)
            if only_owner:
                if user.status in ChatMemberStatus.OWNER:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await msg.reply_text(
                        "ᴏɴʟʏ ᴄʜᴀᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ."
                    )

            if only_dev:
                if user.id in Config.DEV_USERS:
                    return await func(abg, message, *args, **kwargs)
                else:
                    return await msg.reply_text(
                        "ᴏɴʟʏ ʙᴏᴛ ᴅᴇᴠ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ",
                    )

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
                elif permissions == "can_manage_topics":
                    no_permission = "ᴍᴀɴᴀɢᴇ ᴛᴏᴘɪᴄs"
                elif permissions == "is_anonymous":
                    no_permission = "ʀᴇᴍᴀɪɴ ᴀɴᴏɴʏᴍᴏᴜs"
                if is_bot:
                    if (
                        getattr(bot.privileges, permissions)
                        if isinstance(bot.privileges, ChatPrivileges)
                        else False
                    ):
                        return await func(abg, message, *args, **kwargs)
                    elif no_reply:
                        return await msg.answer(
                            f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}",
                            show_alert=True,
                        )
                    else:
                        return await message.reply_text(
                            f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                if is_user:
                    if (
                        getattr(user.privileges, permissions)
                        if isinstance(user.privileges, ChatPrivileges)
                        else False
                    ):
                        return await func(abg, message, *args, **kwargs)
                    elif no_reply:
                        return await msg.answer(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}",
                            show_alert=True,
                        )
                    else:
                        return await message.reply_text(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                if is_both:
                    if (
                        getattr(bot.privileges, permissions)
                        if isinstance(bot.privileges, ChatPrivileges)
                        else False
                    ):
                        pass
                    elif no_reply:
                        return await msg.answer(
                            f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}",
                            show_alert=True,
                        )
                    else:
                        return await message.reply_text(
                            f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )

                    if (
                        getattr(user.privileges, permissions)
                        if isinstance(user.privileges, ChatPrivileges)
                        else False
                    ):
                        pass
                    elif no_reply:
                        return await msg.answer(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}",
                            show_alert=True,
                        )
                    else:
                        return await message.reply_text(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                    return await func(abg, message, *args, **kwargs)
                else:
                    if is_bot:
                        if bot.status == ChatMemberStatus.ADMINISTRATOR:
                            return await func(abg, message, *args, **kwargs)
                        else:
                            return await message.reply_text("ɪ'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")
                    elif is_user:
                        if user.status in [
                            ChatMemberStatus.ADMINISTRATOR,
                            ChatMemberStatus.OWNER,
                        ]:
                            return await func(abg, message, *args, **kwargs)
                        else:
                            return await message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")
                    elif is_both:
                        if user.status == ChatMemberStatus.ADMINISTRATOR:
                            pass
                        else:
                            return await message.reply_text("ɪ'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")

                        if user.status in [
                            ChatMemberStatus.ADMINISTRATOR,
                            ChatMemberStatus.OWNER,
                        ]:
                            pass
                        else:
                            return await message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")
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
