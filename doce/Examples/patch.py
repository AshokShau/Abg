from hydrogram import Client
from hydrogram.types import Message

from . import app


@app.on_cmd(["start", "help"])
async def my_info(self: Client, ctx: Message):
    # for anonymous user
    if not ctx.from_user:
        return
    # Conversation
    name = await ctx.chat.ask("Type Your Name")
    age = await ctx.chat.ask("Type your age")
    add = await ctx.chat.ask("Type your address")
    # : ( if you no need like this you can use : await ctx.reply_text(...) hydrogram method
    await self.send_msg(
        chat_id=ctx.chat.id,
        text=f"Your name is: {name.text}\nYour age is: {age.text}\nyour address is: {add.text}",
    )
