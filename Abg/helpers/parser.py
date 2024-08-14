from html import escape
from re import compile as compiler
from re import sub


async def cleanhtml(raw_html: str) -> str:
    cleaner = compiler("<.*?>")
    return sub(cleaner, "", raw_html)


async def escape_markdown(text: str) -> str:
    escape_chars = r"\*_`\["
    return sub(r"([%s])" % escape_chars, r"\\\1", text)


async def mention_html(name: str, user_id: int) -> str:
    name = escape(name)
    return f'<a href="tg://user?id={user_id}">{name}</a>'


async def mention_markdown(name: str, user_id: int) -> str:
    return f"[{(await escape_markdown(name))}](tg://user?id={user_id})"


# Clean File
async def remove_markdown_and_html(text: str) -> str:
    return await clean_markdown(await clean_html(text))


async def clean_html(text: str) -> str:
    return (
        text.replace("<code>", "")
        .replace("</code>", "")
        .replace("<b>", "")
        .replace("</b>", "")
        .replace("<i>", "")
        .replace("</i>", "")
        .replace("<u>", "")
        .replace("</u>", "")
    )


async def clean_markdown(text: str) -> str:
    return text.replace("`", "").replace("**", "").replace("__", "")
