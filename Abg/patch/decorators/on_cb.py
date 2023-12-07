import asyncio
import typing
from logging import getLogger

import hydrogram
from hydrogram import Client
from hydrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    Forbidden,
    MessageIdInvalid,
    MessageNotModified,
)
from hydrogram.methods import Decorators

from .utils import handle_error

LOGGER = getLogger(__name__)


def callback(
    self,
    data: typing.Union[str, list],
    is_bot: typing.Union[bool, bool] = False,
    is_user: typing.Union[bool, bool] = False,
    filtercb: typing.Union[hydrogram.filters.Filter] = None,
    *args,
    **kwargs,
):
    """
    ### `Client.on_cb("etc")`

    - A decorater to Register Callback Quiries in simple way and manage errors in that Function itself, alternative for `@hydrogram.Client.on_callback_query(hydrogram.filters.regex('^data.*'))`
    - Parameters:
    - data (str || list):
        - The callback query to be handled for a function

    - is_bot (bool) **optional**:
        - If True, the command will only executeed if the Bot is Admin in the Chat, By Default False

    - is_user (bool) **optional**:
        - If True, the command will only executeed if the User is Admin in the Chat, By Default False

    - filter (`~hydrogram.filters`) **optional**:
        - hydrogram Filters, hope you know about this, for Advaced usage. Use `and` for seaperating filters.

    #### Example
    .. code-block:: python
        import hydrogram

        app = hydrogram.Client()

        @app.on_cmd("start")
        async def start(client, message):
            await message.reply_text(
            f"Hello {message.from_user.mention}",
            reply_markup=hydrogram.types.InlineKeyboardMarkup([[
                hydrogram.types.InlineKeyboardButton(
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
        filtercb = hydrogram.filters.regex(f"^{data}.*") & args["filter"]
    else:
        filtercb = hydrogram.filters.regex(f"^{data}.*")

    def wrapper(func):
        async def decorator(abg: Client, q: hydrogram.types.CallbackQuery):
            if is_bot:
                me = await abg.get_chat_member(
                    q.message.chat.id, (await abg.get_me()).id
                )
                if me.status not in (
                    hydrogram.enums.ChatMemberStatus.OWNER,
                    hydrogram.enums.ChatMemberStatus.ADMINISTRATOR,
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
                    hydrogram.enums.ChatMemberStatus.OWNER,
                    hydrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await q.message.edit_text(
                        "ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ"
                    )
            try:
                await func(abg, q, *args, **kwargs)
            except FloodWait as fw:
                LOGGER.warning(str(fw))
                await asyncio.sleep(fw.value)
                LOGGER.info(f"Sleeping for {fw.value}, Due to flood")
            except (MessageIdInvalid, MessageNotModified):
                pass
            except (Forbidden, ChatAdminRequired):
                LOGGER.info(
                    f"Bot cannot write in chat: {q.message.chat.title} [{q.message.chat.id}] or need administration."
                )
                return await q.answer(
                    "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.", show_alert=True
                )
            except BaseException as e:
                return await handle_error(e, q)

        self.add_handler(hydrogram.handlers.CallbackQueryHandler(decorator, filtercb))
        return decorator

    return wrapper


Decorators.on_cb = callback
