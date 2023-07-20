import contextlib
import os
import traceback
import logging
import typing
from datetime import datetime

import pyrogram

from Abg.config import Config

LOGGER = logging.getLogger(__name__)
log_chat = Config.OWNER_ID if Config.LOGGER_ID is None else Config.LOGGER_ID


async def handle_error(
    _, m: typing.Union[pyrogram.types.Message, pyrogram.types.CallbackQuery]
): 
    day = datetime.now()
    tgl_now = datetime.now()
    cap_day = f"{day.strftime('%A')}, {tgl_now.strftime('%d %B %Y %H:%M:%S')}"
    f_errname = f"crash_{tgl_now.strftime('%d %B %Y')}.txt"
    LOGGER.error(traceback.format_exc())
    with open(f_errname, "w+", encoding="utf-8") as log:
        log.write(traceback.format_exc())
        log.close()
    if isinstance(m, pyrogram.types.Message):
        with contextlib.suppress(Exception):
            await m.reply_text(
                "ᴇʀʀᴏʀ ғᴏᴜɴᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ᴄᴏᴍᴍᴀɴᴅ.\nsᴏʀʀʏ ғᴏʀ ɪɴᴄᴏɴᴠᴇɴɪᴇɴᴄᴇ"
            )
            await m._client.send_document(
                log_chat,
                f_errname,
                caption=f"ᴄʀᴀsʜ ʀᴇᴘᴏʀᴛ ᴏғ ᴛʜɪs ʙᴏᴛ\n{cap_day}",
            )
    if isinstance(m, pyrogram.types.CallbackQuery):
        with contextlib.suppress(Exception):
            await m.message.delete()
            await m.message.reply_text(
                "ᴇʀʀᴏʀ ғᴏᴜɴᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ᴄᴏᴍᴍᴀɴᴅ.\nsᴏʀʀʏ ғᴏʀ ɪɴᴄᴏɴᴠᴇɴɪᴇɴᴄᴇ"
            )
            await m.message._client.send_document(
                log_chat,
                f_errname,
                caption=f"ᴄʀᴀsʜ ʀᴇᴘᴏʀᴛ ᴏғ ᴛʜɪs ʙᴏᴛ\n{cap_day}",
            )
    if os.path.exists(f_errname):
        os.remove(f_errname)
    return True
