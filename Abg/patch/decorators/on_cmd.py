import asyncio
import typing
from logging import getLogger

from Abg.config import Config

try:
    import pyrogram
    from pyrogram import errors
except ImportError:
    import hydrogram as pyrogram
    from hydrogram import errors

HANDLER = Config.HANDLER
LOGGER = getLogger(__name__)


def command(
        self,
        cmd: typing.Union[str, list],
        is_disabled: bool = False,
        pm_only: bool = False,
        group_only: bool = False,
        self_admin: bool = False,
        self_only: bool = False,
        handler: typing.Optional[list] = None,
        filtercmd: typing.Optional[pyrogram.filters.Filter] = None,
        *args,
        **kwargs,
) -> typing.Callable[[typing.Callable[[pyrogram.Client, pyrogram.types.Message], typing.Any]], typing.Callable[
    [pyrogram.Client, pyrogram.types.Message], typing.Any]]:
    """
    ### `@Client.on_cmd` - A Decorator to Register Commands in a simple way and manage errors in that Function itself,
    alternative for `@hydrogram.Client.on_message(hydrogram.filters.command('command'))`
    - Parameters: - cmd (str ||
    list): - The command to be handled for a function

    - group_only (bool) **optional**:
        - If True, the command will only executed in Groups only, By Default, False.

    - pm_only (bool) **optional**:
        - If True, the command will only executed in Private Messages only, By Default, False.

    - self_only (bool) **optional**:
        - If True, the command will only execute if used by Self only, By Default False.

    - handler (list) **optional**:
        - If set, the command will be handled by the specified Handler, By Default `Config.HANDLERS`.

    - self_admin (bool) **optional**:
        - If True, the command will only be executed if the Bot is Admin in the Chat, By Default, False

    - filtercmd (`~hydrogram.filters`) **optional**:
        - hydrogram Filters, hope you know about this, for Advanced usage.
        Use `and` for seaperating filters.

    #### Example.
    Code-block:: python
        import hydrogram

        App = hydrogram.Client(.)

        @app.on_cmd("start", is_disabled=False, group_only=False, pm_only=False,
        self_admin=False, self_only=False, filtercmd=hydrogram.filters.chat("777000")
        and hydrogram.filters.text)
        async def start(abg: Client, message):
            await message.reply_text(f" Hello {message.from_user.mention}")
    """
    if handler is None:
        handler = HANDLER

    if filtercmd:
        if self_only:
            filtercmd = (
                    pyrogram.filters.command(cmd, prefixes=handler)
                    & filtercmd
                    & pyrogram.filters.me
            )
        else:
            filtercmd = (
                    pyrogram.filters.command(cmd, prefixes=handler)
                    & filtercmd
            )
    else:
        if self_only:
            filtercmd = (
                    pyrogram.filters.command(cmd, prefixes=handler) & pyrogram.filters.me
            )
        else:
            filtercmd = pyrogram.filters.command(cmd, prefixes=handler)

    def wrapper(func):
        async def decorator(abg: pyrogram.Client, message: pyrogram.types.Message):
            if is_disabled:
                return await message.reply_text(
                    "This command is disabled by the Admins."
                )

            if group_only and message.chat.type not in (
                    pyrogram.enums.ChatType.GROUP,
                    pyrogram.enums.ChatType.SUPERGROUP,
            ):
                return await message.reply_text(
                    "This command can be used in supergroups only."
                )

            if self_admin:
                me = await abg.get_chat_member(message.chat.id, (await abg.get_me()).id)
                if me.status not in (
                        pyrogram.enums.ChatMemberStatus.OWNER,
                        pyrogram.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await message.reply_text(
                        "I must be admin to execute this command."
                    )

            if pm_only and message.chat.type != pyrogram.enums.ChatType.PRIVATE:
                return await message.reply_text("This command can be used in PM only.")

            try:
                await func(abg, message, *args, **kwargs)
            except pyrogram.StopPropagation:
                raise pyrogram.StopPropagation  # Stop Propagation
            except pyrogram.ContinuePropagation:
                pass  # Do nothing
            except errors.FloodWait as fw:
                LOGGER.warning("Sleeping for {fw.value}, Due to flood")
                await asyncio.sleep(fw.value)
            except (errors.Forbidden, errors.SlowmodeWait):
                LOGGER.warning(
                    f"Forbidden : {message.chat.title} [{message.chat.id}] doesn't have write permission."
                )
                return  # await message.chat.leave()
            except Exception as e:
                return LOGGER.error(f"Error while executing command: {e}")

        self.add_handler(
            pyrogram.handlers.MessageHandler(callback=decorator, filters=filtercmd)
        )
        return decorator

    return wrapper


pyrogram.methods.Decorators.on_cmd = command
