from hydrogram import Client
from hydrogram.helpers import ikb
from hydrogram.types import CallbackQuery, Message

from Abg import *  # type: ignore

app = Client(
    name='Abg',
    api_id=6,
    api_hash='eb06d4abfb49dc3eeb1aeb98ae0f581e',
    bot_token="TOKEN",
    in_memory=True,
)


@app.on_cmd("start")
async def start(self: Client, ctx: Message):
    """
    Sends a Hello World message with an inline button that triggers the hello callback.
    """
    await ctx.reply_text(
        "Hello World",
        reply_markup=ikb([[("Hello", "hello")]])
    )


@app.on_cb("hello")
async def hello(_: Client, q: CallbackQuery):
    """
    Called when the user presses the "Hello" button in the start command.
    """
    await q.answer("Hello From Abg", show_alert=True)


@app.on_cmd("del", group_only=True)
@app.adminsOnly(
    permissions=["can_delete_messages", "can_restrict_members"],
    is_both=True,
)
async def del_msg(self: Client, m: Message):
    """
    Deletes a message from the chat.

    If the message is a reply to another message, it deletes that message too.
    """
    if m.reply_to_message:
        # Delete the replied message
        await self.delete_messages(
            chat_id=m.chat.id,
            message_ids=[m.reply_to_message.id],
        )
        # Delete the command message
        await m.delete()
    else:
        # If the message is not a reply, reply with an error message
        await m.reply_text(text="You need to reply to a message to delete it.", quote=True)


if __name__ == "__main__":
    print("Running...")
    app.run()
