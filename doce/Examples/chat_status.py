from hydrogram import Client
from hydrogram.types import Message

from . import app


@app.on_cmd("del")
@app.adminsOnly(permissions="can_delete_messages", is_both=True)
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
