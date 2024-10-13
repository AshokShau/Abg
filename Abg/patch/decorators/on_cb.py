import asyncio
import typing
from logging import getLogger

try:
    import pyrogram
    from pyrogram import errors
except ImportError:
    import hydrogram as pyrogram
    from hydrogram import errors

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
    ### `Client.on_cb("data")`

    - A decorator to Register Callback Quires in simple way and manage errors in that Function itself, alternative
    for `@hydrogram.Client.on_callback_query(hydrogram.filters.regex('^data.*'))`
    - Parameters: - data (str || list):
    - The callback query to be handled for a function

    - Is_bot (bool) **optional**:
        - If True, the command will only be executed if the Bot is Admin in the Chat, By Default, False

    - Is_user (bool) **optional**:
        - If True, the command will only be executed if the User is Admin in the Chat, By Default, False

    - Filter (`~hydrogram.filters`) **optional**:
        - hydrogram Filters, hope you know about this, for Advanced usage.
        Use `and` for exasperating filters.

    #### Example.
    Code-block:: python
        import hydrogram

        app = pyrogram.Client()

        @app.on_cmd("start")
        async def start(client, message):
            await message.reply_text(
            f" Hello {message.from_user.mention}",
            reply_markup=hydrogram.types.InlineKeyboardMarkup([[
                hydrogram.types.InlineKeyboardButton("Click Here",
                "data"
                )
            ]])
            )

        @app.on_cb("data")
        async def data(client, CallbackQuery):
        await CallbackQuery.answer("Hello: /", show_alert=True)
    """
    if filtercb:
        filtercb = pyrogram.filters.regex(f"^{data}.*") & args["filter"]
    else:
        filtercb = pyrogram.filters.regex(f"^{data}.*")

    def wrapper(func):
        async def decorator(abg: pyrogram.Client, q: pyrogram.types.CallbackQuery):
            if is_bot:
                me = await abg.get_chat_member(
                    q.message.chat.id, (await abg.get_me()).id
                )
                if me and me.status not in (
                        pyrogram.enums.ChatMemberStatus.OWNER,
                        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await q.message.edit_text(
                        "I must be admin to execute this command."
                    )
            if is_user:
                try:
                    user = await q.message.chat.get_member(q.from_user.id)
                except Exception as e:
                    LOGGER.error("Error while fetching user status: " + str(e))
                    return
                if user and user.status not in (
                        pyrogram.enums.ChatMemberStatus.OWNER,
                        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await q.message.edit_text(
                        "You must be admin to execute this command."
                    )
            try:
                await func(abg, q, *args, **kwargs)
            except errors.FloodWait as fw:
                LOGGER.warning(str(fw))
                await asyncio.sleep(fw.value)
                LOGGER.info(f"Sleeping for {fw.value}, Due to flood")
            except (errors.MessageIdInvalid, errors.MessageNotModified):
                pass
            except (errors.Forbidden, errors.ChatAdminRequired):
                LOGGER.warning(
                    f"Bot cannot write in chat: {q.message.chat.title} [{q.message.chat.id}] or need administration."
                )
                return await q.answer(
                    "I must be admin to execute this command.", show_alert=True
                )
            except Exception as e:
                LOGGER.error(f"Error while executing command: {e}")
                return

        self.add_handler(pyrogram.handlers.CallbackQueryHandler(decorator, filtercb))
        return decorator

    return wrapper


pyrogram.methods.Decorators.on_cb = callback
