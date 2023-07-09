import asyncio
import typing
from logging import getLogger

import pyrogram
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    Forbidden,
    MessageNotModified,
    SlowmodeWait,
)
from pyrogram.methods import Decorators

LOGGER = getLogger(__name__)


def callback(
    self,
    data: typing.Union[str, list],
    self_admin: typing.Union[bool, bool] = False,
    filter: typing.Union[pyrogram.filters.Filter, pyrogram.filters.Filter] = None,
    *args,
    **kwargs,
):
    """
    ### `Client.on_cb("etc")`

    - A decorater to Register Callback Quiries in simple way and manage errors in that Function itself, alternative for `@pyrogram.Client.on_callback_query(pyrogram.filters.regex('^data.*'))`
    - Parameters:
    - data (str || list):
        - The callback query to be handled for a function

    - self_admin (bool) **optional**:
        - If True, the command will only executeed if the Bot is Admin in the Chat, By Default False

    - filter (`~pyrogram.filters`) **optional**:
        - Pyrogram Filters, hope you know about this, for Advaced usage. Use `and` for seaperating filters.

    #### Example
    .. code-block:: python
        import pyrogram

        app = pyrogram.Client()

        @app.command("start")
        async def start(client, message):
            await message.reply_text(
            f"Hello {message.from_user.mention}",
            reply_markup=pyrogram.types.InlineKeyboardMarkup([[
                pyrogram.types.InlineKeyboardButton(
                "Click Here",
                "data"
                )
            ]])
            )

        @app.on_cb("data")
        async def data(client, CallbackQuery):
        await CallbackQuery.answer("Hello :)", show_alert=True)
    """
    if filter:
        filter = pyrogram.filters.regex(f"^{data}.*") & args["filter"]
    else:
        filter = pyrogram.filters.regex(f"^{data}.*")

    def wrapper(func):
        async def decorator(client, CallbackQuery: pyrogram.types.CallbackQuery):
            if self_admin:
                me = await client.get_chat_member(
                    CallbackQuery.message.chat.id, (await client.get_me()).id
                )
                if me.status not in (
                    pyrogram.enums.ChatMemberStatus.OWNER,
                    pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await CallbackQuery.message.edit_text(
                        "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ"
                    )
            try:
                await func(client, CallbackQuery)
            except FloodWait as fw:
                LOGGER.warning(str(fw))
                await asyncio.sleep(fw.value)
            except MessageNotModified:
                LOGGER.info(
                    "The message was not modified because you tried to edit it using the same content "
                )
            except (Forbidden, SlowmodeWait, ChatAdminRequired):
                LOGGER.info(
                    f"You cannot write in this chat: {CallbackQuery.message.chat.title} [{CallbackQuery.message.chat.id}]"
                )
            except BaseException as e:
                LOGGER.error(f"Error Found in callback Handler : {e}")
                return await CallbackQuery.message.edit_text(f"ᴇʀʀᴏʀ ғᴏᴜɴᴅ:\n{e}")

        self.add_handler(pyrogram.handlers.CallbackQueryHandler(decorator, filter))
        return decorator

    return wrapper


Decorators.on_cb = callback
