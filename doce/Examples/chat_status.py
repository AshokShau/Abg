from pyrogram import Client
from pyrogram.types import Message

from Abg.chat_status import adminsOnly

from . import app


@app.on_cmd("del")
@adminsOnly("can_delete_messages")  # user need to msg delete rights
async def del_msg(c: Client, m: Message):
    if m.reply_to_message:
        await m.delete()
        await c.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id,
        )
    else:
        await m.reply_text(text="ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ ᴡᴀɴɴᴀ ᴅᴇʟᴇᴛᴇ?")
    return
