from hydrogram.errors import MessageNotModified
from hydrogram.types import CallbackQuery, Message

from Abg.helpers import ikb

from . import app


async def gen_settings_kb(q: Message or CallbackQuery):
    return ikb(
        [
            [
                ("⚫", "callback"),
            ],
            [("⛔", "callback_x")],
        ],
    )


@app.on_cmd(["settings", "setting"])
async def settings_(c: app, m: Message):
    await m.reply_text(
        f"**sᴇᴛᴛɪɴɢs**\nᴄʜᴀᴛ: {m.chat.id}\n",
        reply_markup=(await gen_settings_kb(m)),
    )
    return


# callback
@app.on_cb("setting")
async def setting_CB(c: app, q: CallbackQuery):
    data = q.data.split(".")[1]
    # kb = ikb([[("ʙᴀᴄᴋ", "setting.back")]])
    if data == "back":
        try:
            await q.message.edit_text(
                text=f"**sᴇᴛᴛɪɴɢs**\nᴄʜᴀᴛ: {q.message.chat.id}\n",
                reply_markup=(await gen_settings_kb(q.message)),
            )
        except MessageNotModified:
            pass
        await q.answer()
        return
