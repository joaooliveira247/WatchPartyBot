from .src. discord_bot import DiscordBot
from typer import Typer, Option
from typing import Optional
import json
from .config import settings

main = Typer()

@main.command()
def init(token: Optional[str] = None) -> Typer:
    client = DiscordBot()
    if token:
        with open(
            "./watchparty_bot/.secrets.json", "w",encoding="utf-8"
            ) as secret:
            json.dump(
                {"token": token},
                secret,
                )
    client.run(settings.token)

