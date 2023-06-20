from functools import partial, wraps
from typing import Iterable, Optional, Union

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import CallbackQuery, Message

group_types: Iterable[ChatType] = (ChatType.GROUP, ChatType.SUPERGROUP)

admin_status: Iterable[ChatMemberStatus] = (
    ChatMemberStatus.OWNER,
    ChatMemberStatus.ADMINISTRATOR,
)


async def check_perms(
    message: Union[CallbackQuery, Message],
    permissions: Optional[Union[list, str]],
    complain_perms: bool,
) -> bool:
    if isinstance(message, CallbackQuery):
        sender = partial(message.answer, show_alert=True)
        chat = message.message.chat
    else:
        sender = message.reply_text
        chat = message.chat

    # TODO : ғᴏʀ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ :( ɪғ ᴜ ᴄᴀɴ ᴛʀʏ ᴘᴜʟʟ

    user = await chat.get_member(message.from_user.id)
    if user.status == ChatMemberStatus.OWNER:
        return True

    # ɴᴏ ᴘᴇʀᴍɪssɪᴏɴs sᴘᴇᴄɪғɪᴇᴅ, ᴀᴄᴄᴇᴘᴛ ʙᴇɪɴɢ ᴀɴ ᴀᴅᴍɪɴ.
    if not permissions and user.status == ChatMemberStatus.ADMINISTRATOR:
        return True

    if user.status != ChatMemberStatus.ADMINISTRATOR:
        if complain_perms:
            await sender("ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return False

    if isinstance(permissions, str):
        permissions = [permissions]

    missing_perms = [
        permission
        for permission in permissions
        if not getattr(user.privileges, permission)
    ]

    if not missing_perms:
        return True
    if complain_perms:
        await sender(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴘᴇʀᴍɪssɪᴏɴs: {permissions}".format(
                permissions=", ".join(missing_perms)
            )
        )
    return False


"""
@adminsOnly("permissions")

can_manage_chat (bool, optional) – True, if the administrator can access the chat event log, chat statistics, message statistics in channels, see channel members, see anonymous administrators in supergroups and ignore slow mode. Implied by any other administrator privilege.

can_delete_messages (bool, optional) – True, if the administrator can delete messages of other users.

can_manage_video_chats (bool, optional) – Groups and supergroups only. True, if the administrator can manage video chats (also called group calls).

can_restrict_members (bool, optional) – True, if the administrator can restrict, ban or unban chat members.

can_promote_members (bool, optional) – True, if the administrator can add new administrators with a subset of his own privileges or demote administrators that he has promoted, directly or indirectly (promoted by administrators that were appointed by the user).

can_change_info (bool, optional) – True, if the user is allowed to change the chat title, photo and other settings.

can_post_messages (bool, optional) – Channels only. True, if the administrator can post messages in the channel.

can_edit_messages (bool, optional) – Channels only. True, if the administrator can edit messages of other users and can pin messages.

can_invite_users (bool, optional) – True, if the user is allowed to invite new users to the chat.

can_pin_messages (bool, optional) – Groups and supergroups only. True, if the user is allowed to pin messages.

is_anonymous (bool, optional) – True, if the user’s presence in the chat is hidden.
"""


def adminsOnly(
    permissions: Union[list, str] = None,
    allow_pm: bool = False,
    complain_perms: bool = True,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            client: Client, message: Union[CallbackQuery, Message], *args, **kwargs
        ):
            if isinstance(message, CallbackQuery):
                sender = partial(message.answer, show_alert=True)
                msg = message.message
            elif isinstance(message, Message):
                sender = message.reply_text
                msg = message
            else:
                raise NotImplementedError(
                    f"require_admin ᴄᴀɴ'ᴛ ᴘʀᴏᴄᴇss ᴜᴘᴅᴀᴛᴇs ᴡɪᴛʜ ᴛʜᴇ ᴛʏᴘᴇ '{message.__name__}' yet."
                )

            if msg.chat.type == ChatType.PRIVATE:
                if allow_pm:
                    return await func(client, message, *args, *kwargs)
                return await sender(
                    "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ'ᴛ ʙᴇ ᴜsᴇᴅ ɪɴ ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ. ɪғ ʏᴏᴜ ɴᴇᴇᴅ ᴀɴʏ ʜᴇʟᴘ, ᴘʟᴇᴀsᴇ ᴜsᴇ ᴛʜᴇ <code>/help</code> ᴄᴏᴍᴍᴀɴᴅ"
                )
            if msg.chat.type == ChatType.CHANNEL:
                return await func(client, message, *args, *kwargs)
            has_perms = await check_perms(message, permissions, complain_perms)
            if has_perms:
                return await func(client, message, *args, *kwargs)

        return wrapper

    return decorator
