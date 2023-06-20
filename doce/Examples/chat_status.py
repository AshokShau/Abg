from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message

from Abg.chat_status import adminsOnly, command

from . import app


@app.on_message(command("del"))
@adminsOnly("can_delete_messages")  # user need to delete rights
async def del_msg(c: Client, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        return

    if m.reply_to_message:
        await m.delete()
        await c.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id,
        )
    else:
        await m.reply_text(text="ᴡʜᴀᴛ ᴅᴏ ʏᴏᴜ ᴡᴀɴɴᴀ ᴅᴇʟᴇᴛᴇ?")
    return
