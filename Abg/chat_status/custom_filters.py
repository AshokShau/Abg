from re import compile as compile_re
from re import escape
from shlex import split
from typing import List, Union

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType
from pyrogram.errors import UserNotParticipant
from pyrogram.filters import create
from pyrogram.types import Message

PREFIX_HANDLER = ["/", "!", "~", ".", "+", "*"]


def command(
    commands: Union[str, List[str]],
    case_sensitive: bool = False,
):
    async def func(flt, c: Client, m: Message):
        if not m:
            return

        date = m.edit_date
        if date:
            return  # reaction

        if m.chat and m.chat.type == ChatType.CHANNEL:
            return

        if m and not m.from_user:
            return False

        if m.from_user.is_bot:
            return False

        if any([m.forward_from_chat, m.forward_from]):
            return False

        text: str = m.text or m.caption
        if not text:
            return False
        regex = r"^[{prefix}](\w+)(@{bot_name})?(?: |$)(.*)".format(
            prefix="|".join(escape(x) for x in PREFIX_HANDLER),
            bot_name=c.me.username,
        )
        matches = compile_re(regex).search(text)
        if matches:
            m.command = [matches.group(1)]
            if matches.group(1) not in flt.commands:
                return False
            if bool(m.chat and m.chat.type in {ChatType.SUPERGROUP}):
                try:
                    user_status = (await m.chat.get_member(m.from_user.id)).status
                except UserNotParticipant:
                    # i.e anon admin
                    user_status = CMS.ADMINISTRATOR
                except ValueError:
                    # i.e. PM
                    user_status = CMS.OWNER
            if matches.group(3) == "":
                return True
            try:
                for arg in split(matches.group(3)):
                    m.command.append(arg)
            except ValueError:
                pass
            return True
        return False

    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    return create(
        func,
        "NormalCommandFilter",
        commands=commands,
        case_sensitive=case_sensitive,
    )
