import asyncio
import contextlib
import logging
import os
import traceback
import typing
from datetime import datetime

import pyrogram
from pyrogram import filters
from pyrogram.errors import MessageDeleteForbidden

from Abg.config import Config

LOGGER = logging.getLogger(__name__)
log_chat = Config.OWNER_ID if Config.LOGGER_ID is None else Config.LOGGER_ID

data = {}


async def task(msg, warn=False, sec=None):
    if warn:
        user = msg.from_user or msg.sender_chat
        ids = await msg.reply_msg(
            f"sᴏʀʀʏ {user.mention if msg.from_user else msg.sender_chat.title} , ʏᴏᴜ ᴍᴜsᴛ ᴡᴀɪᴛ ғᴏʀ {sec}s ʙᴇғᴏʀᴇ ᴜsɪɴɢ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ᴀɢᴀɪɴ.."
        )
        try:
            await msg.delete_msg()
        except MessageDeleteForbidden:
            pass
        await asyncio.sleep(sec)
        await ids.edit_msg(
            f"ᴀʟʀɪɢʜᴛ {user.mention if msg.from_user else msg.sender_chat.title} , ʏᴏᴜʀ ᴄᴏᴏʟᴅᴏᴡɴ ɪs ᴏᴠᴇʀ ʏᴏᴜ ᴄᴀɴ ᴄᴏᴍᴍᴀɴᴅ ᴀɢᴀɪɴ.",
            del_in=3,
        )


def wait(sec):
    async def ___(flt, _, msg):
        user_id = msg.from_user.id if msg.from_user else msg.sender_chat.id
        if user_id in data:
            if msg.date.timestamp() >= data[user_id]["timestamp"] + flt.data:
                data[user_id] = {"timestamp": msg.date.timestamp(), "warned": False}
                return True
            else:
                if not data[user_id]["warned"]:
                    data[user_id]["warned"] = True
                    asyncio.ensure_future(
                        task(msg, True, flt.data)
                    )  # for super accuracy use (future - time.time())
                    return False  # cause we dont need delete again

                asyncio.ensure_future(task(msg))
                return False
        else:
            data.update({user_id: {"timestamp": msg.date.timestamp(), "warned": False}})
            return True

    return filters.create(___, data=sec)


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
