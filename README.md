# ᴀʙɢ :->
> 
### • Conversation ingram

```python
from pyrogram import filters, Client
from pyrogram.types import Message
from Abg import patch  # type : ignore

app = Client("my_account")

@app.on_message(filters.command(["myinfo"]))
async def my_info(self: Client, ctx: Message):
    if not ctx.from_user:
        return
    name = await ctx.chat.ask("Type Your Name")
    age = await ctx.chat.ask("Type your age")
    add = await ctx.chat.ask("Type your address")
    # you can also use : ctx.reply_text(...)
    await self.send_msg(
        chat_id=ctx.chat.id,
        text=f"Your name is: {name.text}\nYour age is: {age.text}\nyour address is: {add.text}",
    )

  app.run()
```
>
### • User Rights 

```python 
from Abg.chat_status import adminsOnly, command
from pyrogram.enums import ChatType
from pyrogram.types import Message
from pyrogram import Client

app = Client("my_account")

@app.on_message(command("del"))
@adminsOnly("can_delete_messages")
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
  
  app.run()
```


>
### • Keyboards

```python
from Abg.inline import InlineKeyboard, InlineButton


keyboard = InlineKeyboard(row_width=3)
keyboard.add(
    InlineButton('1', 'inline_keyboard:1'),
    InlineButton('2', 'inline_keyboard:2'),
    InlineButton('3', 'inline_keyboard:3'),
    InlineButton('4', 'inline_keyboard:4'),
    InlineButton('5', 'inline_keyboard:5'),
    InlineButton('6', 'inline_keyboard:6'),
    InlineButton('7', 'inline_keyboard:7')
)
```

#### Result

<p><img src="https://raw.githubusercontent.com/Abishnoi69/Abg/master/doce/images/add_inline_button.png" alt="add_inline_button"></p>


### ɪɴsᴛᴀʟʟɪɴɢ :->

```bash
pip3 install Abg
```

━━━━━━━━━━━━━━━━━━━━
## ɴᴏᴛᴇ :->

- This library is made for my personal Project so don't take it deeply  [you can use this 24*7 running ] 
- My Project [@AbgRobot](https://t.me/AbgRobot) / [@Exon_Robot](https://t.me/Exon_Robot) & [@ExonMusicBot](https://t.me/ExonMusicBot)

- ᴇɴᴊᴏʏ ʙᴀʙʏ ♡ 

━━━━━━━━━━━━━━━━━━━━ 

