from hydrogram import Client

from Abg import patch  # type : ignore

app = Client(
    ":Abg",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
)

app.start()
