from .src.discord_bot import bot
from typer import Typer, Option
from typing import Optional
import json
from .config import settings

main = Typer()

@main.command(name="init")
def init(token: Optional[str] = None) -> Typer:
    if token:
        with open(
            "./watchparty_bot/.secrets.json", "w",encoding="utf-8"
            ) as secret:
            json.dump(
                {"token": token},
                secret,
                )

    bot.run(settings.token)

