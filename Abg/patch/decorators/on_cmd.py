import asyncio
import typing
from logging import getLogger

import pyrogram
from pyrogram import Client
from pyrogram.errors import FloodWait, Forbidden, SlowmodeWait
from pyrogram.methods import Decorators

from .utils import handle_error

HANDLER = ["/", "!", "~", ".", "+", "*", "$", " @"]

LOGGER = getLogger(__name__)


def command(
    self,
    command: typing.Union[str, list],
    is_disabled: typing.Union[bool, bool] = False,
    pm_only: typing.Union[bool, bool] = False,
    group_only: typing.Union[bool, bool] = False,
    self_admin: typing.Union[bool, bool] = False,
    self_only: typing.Union[bool, bool] = False,
    handler: typing.Optional[list] = None,
    filter: typing.Union[pyrogram.filters.Filter, pyrogram.filters.Filter] = None,
    *args,
    **kwargs,
):
    """
    ### `@Client.on_cmd`
    - A decorater to Register Commands in simple way and manage errors in that Function itself, alternative for `@pyrogram.Client.on_message(pyrogram.filters.command('command'))`
    - Parameters:
    - command (str || list):
        - The command to be handled for a function

    - group_only (bool) **optional**:
        - If True, the command will only executed in Groups only, By Default False.

    - pm_only (bool) **optional**:
        - If True, the command will only executed in Private Messages only, By Default False.

    - self_only (bool) **optional**:
        - If True, the command will only excute if used by Self only, By Default False.

    - handler (list) **optional**:
        - If set, the command will be handled by the specified Handler, By Default `Config.HANDLERS`.

    - self_admin (bool) **optional**:
        - If True, the command will only executeed if the Bot is Admin in the Chat, By Default False

    - filter (`~pyrogram.filters`) **optional**:
        - Pyrogram Filters, hope you know about this, for Advaced usage. Use `and` for seaperating filters.

    #### Example
    .. code-block:: python
        import pyrogram

        app = pyrogram.Client()

        @app.on_cmd("start", is_disabled=False, group_only=False, pm_only=False, self_admin=False, self_only=False, pyrogram.filters.chat("777000") and pyrogram.filters.text)
        async def start(abg: Client, message):
            await message.reply_text(f"Hello {message.from_user.mention}")
    """
    if handler is None:
        handler = HANDLER
    if filter:
        if self_only:
            filter = (
                pyrogram.filters.command(command, prefixes=handler)
                & filter
                & pyrogram.filters.me
            )
        else:
            filter = (
                pyrogram.filters.command(command, prefixes=handler)
                & filter
                & pyrogram.filters.me
            )
    else:
        if self_only:
            filter = (
                pyrogram.filters.command(command, prefixes=handler)
                & pyrogram.filters.me
            )
        else:
            filter = pyrogram.filters.command(command, prefixes=handler)

    def wrapper(func):
        async def decorator(abg: Client, message: pyrogram.types.Message):
            if is_disabled:
                return await message.reply_text(
                    "sᴏʀʀʏ, ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ʙʏ ᴏᴡɴᴇʀ."
                )
            if self_admin and message.chat.type != pyrogram.enums.ChatType.SUPERGROUP:
                return await message.reply_text(
                    "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ɪɴ sᴜᴘᴇʀɢʀᴏᴜᴘs ᴏɴʟʏ."
                )
            if self_admin:
                me = await abg.get_chat_member(message.chat.id, (await abg.get_me()).id)
                if me.status not in (
                    pyrogram.enums.ChatMemberStatus.OWNER,
                    pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await message.reply_text(
                        "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ"
                    )
            if group_only and message.chat.type != pyrogram.enums.ChatType.SUPERGROUP:
                return await message.reply_text(
                    "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ɪɴ sᴜᴘᴇʀɢʀᴏᴜᴘs ᴏɴʟʏ."
                )
            if pm_only and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ɪɴ ᴘᴍs ᴏɴʟʏ.")
            try:
                await func(abg, message)
            except FloodWait as fw:
                LOGGER.warning(str(fw))
                await asyncio.sleep(fw.value)
            except (Forbidden, SlowmodeWait):
                LOGGER.info(
                    f"Leaving chat : {message.chat.title} [{message.chat.id}], because doesn't have write permission."
                )
                return await abg.leave_chat(message.chat.id)
            except BaseException as e:
                return await handle_error(e, message)

        self.add_handler(
            pyrogram.handlers.MessageHandler(callback=decorator, filters=filter)
        )
        return decorator

    return wrapper


Decorators.on_cmd = command
