<p align="center">
<b> ABG </b>
</p>

<p align="center"><a href="https://pepy.tech/project/abg"> <img src="https://static.pepy.tech/personalized-badge/abg?period=total&units=international_system&left_color=black&right_color=black&left_text=Downloads" width="169" height="29.69" alt="Downloads"/></a></p>

### Requirements 

- Python 3.8 ᴏʀ higher.
- hydrogram 0.0.1 ᴏʀ higher.

### Installing :
> **Note**: If you are using Hydrogram, avoid installing Pyrogram or its forks to prevent potential conflicts.

```bash
pip install -U Abg # For Pyrogram or Pyrogram Forks
```

```bash
pip install -U Abg[hydrogram] # For Hydrogram
```
```bash
pip install -U Abg[pyrofork] # for pyrofork
```


### Getting Started
```python
from hydrogram import Client
from hydrogram.types import CallbackQuery, Message

from Abg import *  # type: ignore
from hydrogram.helpers import ikb

app = Client(
    name='Abg',
    api_id=6,
    api_hash='eb06d4abfb49dc3eeb1aeb98ae0f581e',
    bot_token="TOKEN",
    in_memory=True,
)


@app.on_cmd("start")
async def start(self: Client, ctx: Message):
    await ctx.reply_text("Hello World", reply_markup=ikb([[("Hello", "hello")]]))


@app.on_cb("hello")
async def hello(_: Client, q: CallbackQuery):
    await q.answer("Hello From Abg", show_alert=True)


app.run()

```

#### Permissions Check for Admins
```python
from Abg import *  # type: ignore # (all patch)
from hydrogram.types import Message
from hydrogram import Client

app = Client("my_account")

@app.on_cmd("del", group_only=True)
@adminsOnly(
    self=app,
    permissions="can_delete_messages",
    is_both=True,
) # also you can use like this @app.adminsOnly(permissions="can_delete_messages", is_both=True)
async def del_msg(self: Client, m: Message):
    if m.reply_to_message:
        await m.delete()
        await self.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id,
        )
    else:
        await m.reply_text(text="Reply to a message to delete it")
  
app.run()
```


>
#### keyboard's

```python
from Abg.patch.inline import InlineKeyboard, InlineButton

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
