from html import escape
from re import compile as compiler, sub

# Constants
HTML_TAG_PATTERN = "<.*?>"
ESCAPE_CHARS = r"\*_`\["


# Clean HTML
async def clean_html(raw_html: str) -> str:
    cleaner = compiler(HTML_TAG_PATTERN)
    return sub(cleaner, "", raw_html)


# Escape Markdown
async def escape_markdown(text: str) -> str:
    return sub(r"([%s])" % ESCAPE_CHARS, r"\\\1", text)


# Mention in HTML
async def mention_html(name: str, user_id: int) -> str:
    return f'<a href="tg://user?id={user_id}">{escape(name)}</a>'


# Mention in Markdown
async def mention_markdown(name: str, user_id: int) -> str:
    escaped_name = await escape_markdown(name)
    return f"[{escaped_name}](tg://user?id={user_id})"


# Remove Markdown and HTML
async def remove_markdown_and_html(text: str) -> str:
    cleaned_html = await clean_html(text)
    return await clean_markdown(cleaned_html)


# Clean HTML Tags
async def clean_html_tags(text: str) -> str:
    tags = ["<code>", "</code>", "<b>", "</b>", "<i>", "</i>", "<u>", "</u>"]
    for tag in tags:
        text = text.replace(tag, "")
    return text


# Clean Markdown
async def clean_markdown(text: str) -> str:
    markdown_chars = ["`", "**", "__"]
    for char in markdown_chars:
        text = text.replace(char, "")
    return text
