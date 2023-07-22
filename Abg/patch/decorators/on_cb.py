import asyncio
import typing
from logging import getLogger

import pyrogram
from pyrogram import Client
from pyrogram.errors import ChatAdminRequired, FloodWait, Forbidden, MessageNotModified
from pyrogram.methods import Decorators

from .utils import handle_error

LOGGER = getLogger(__name__)


def callback(
    self,
    data: typing.Union[str, list],
    is_bot: typing.Union[bool, bool] = False,
    is_user: typing.Union[bool, bool] = False,
    filtercb: typing.Union[pyrogram.filters.Filter] = None,
    *args,
    **kwargs,
):
    """
    ### `Client.on_cb("etc")`

    - A decorater to Register Callback Quiries in simple way and manage errors in that Function itself, alternative for `@pyrogram.Client.on_callback_query(pyrogram.filters.regex('^data.*'))`
    - Parameters:
    - data (str || list):
        - The callback query to be handled for a function

    - is_bot (bool) **optional**:
        - If True, the command will only executeed if the Bot is Admin in the Chat, By Default False

    - is_user (bool) **optional**:
        - If True, the command will only executeed if the User is Admin in the Chat, By Default False

    - filter (`~pyrogram.filters`) **optional**:
        - Pyrogram Filters, hope you know about this, for Advaced usage. Use `and` for seaperating filters.

    #### Example
    .. code-block:: python
        import pyrogram

        app = pyrogram.Client()

        @app.on_cmd("start")
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
        await CallbackQuery.answer("Hello :/", show_alert=True)
    """
    if filtercb:
        filtercb = pyrogram.filters.regex(f"^{data}.*") & args["filter"]
    else:
        filtercb = pyrogram.filters.regex(f"^{data}.*")

    def wrapper(func):
        async def decorator(abg: Client, q: pyrogram.types.CallbackQuery):
            if is_bot:
                me = await abg.get_chat_member(
                    q.message.chat.id, (await abg.get_me()).id
                )
                if me.status not in (
                    pyrogram.enums.ChatMemberStatus.OWNER,
                    pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await q.message.edit_text(
                        "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ"
                    )
            if is_user:
                try:
                    user = await q.message.chat.get_member(q.from_user.id)
                except BaseException as e:
                    return await handle_error(e, q)
                if user.status not in (
                    pyrogram.enums.ChatMemberStatus.OWNER,
                    pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await q.message.edit_text(
                        "ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ"
                    )
            try:
                await func(abg, q)
            except FloodWait as fw:
                LOGGER.warning(str(fw))
                await asyncio.sleep(fw.value)
                LOGGER.info(f"Sleeping for {fw.value}, Due to flood")
            except MessageNotModified:
                LOGGER.info(
                    "The message was not modified because you tried to edit it using the same content "
                )
            except (Forbidden, ChatAdminRequired):
                LOGGER.info(
                    f"Bot cannot write in chat: {q.message.chat.title} [{q.message.chat.id}] or need administration."
                )
                return await q.answer(
                    "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.", show_alert=True
                )
            except BaseException as e:
                return await handle_error(e, q)

        self.add_handler(pyrogram.handlers.CallbackQueryHandler(decorator, filtercb))
        return decorator

    return wrapper


Decorators.on_cb = callback
