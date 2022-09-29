from watchparty_bot.src.wrapper import movie_wrapper
from watchparty_bot.src.utils import Utils
from disnake.ext import commands
from disnake import (
    Embed,
    ChannelType,
    Thread,
    Message,
    Colour,
    ApplicationCommandInteraction,
    utils,
    Role
)
from asyncio import sleep
from unicodedata import normalize
from requests import HTTPError

DELETE_AFTER: float = 10.0

bot: commands.Bot = commands.Bot(command_prefix=commands.when_mentioned)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} \U0001f4a1")


@commands.cooldown(rate=2, per=480)
@bot.slash_command(name="ticket")
async def ticket(command: ApplicationCommandInteraction) -> None:
    ...


@ticket.sub_command("get")
async def get_ticket(command: ApplicationCommandInteraction) -> Role:
    for role in command.user.roles:
        if "Viewer" not in role.name:
            await command.response.send_message(
                "received ticket 🎬  |  Viewer", delete_after=DELETE_AFTER
            )
            return await command.author.add_roles(
                utils.get(command.guild.roles, name="🎬  |  Viewer")
            )

    await command.response.send_message(
        "You already have a ticket.", delete_after=DELETE_AFTER
    )


@ticket.sub_command("drop")
async def drop_ticket(command: ApplicationCommandInteraction) -> Message:
    await command.response.send_message(
                "droped ticket 🎬  |  Viewer", delete_after=DELETE_AFTER
            )
    return await command.author.remove_roles(
        utils.get(command.guild.roles, name="🎬  |  Viewer")
    )


@ticket.error
async def ticket_cooldown_error(
    ctx: ApplicationCommandInteraction,
    error: commands.errors.CommandOnCooldown,
) -> Message:
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.response.send_message(
            f"Command on cooldown, "
            f"{Utils.seconds_to_minutes(error.retry_after)} minutes remaning.",
            delete_after=DELETE_AFTER,
        )


    @staticmethod
    def clean_phrase(phrase: str | list[str]) -> str | list[str]:
        if isinstance(phrase, str):
            return (
                normalize("NFD", phrase)
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
        cleaned_phrases = []
        for word in phrase:
            cleaned_phrases.append(Utils.clean_phrase(word))

        return cleaned_phrases

@commands.cooldown(rate=3, per=480, type=commands.BucketType.user)
@bot.slash_command(name="poll", description="Make an poll.")
async def poll(
    command: ApplicationCommandInteraction,
    movies: str = commands.Param(
        name="movies", description="Insert movies titles. Ex: The 100, Dahmer"
        ),
    poll_time: commands.Range[10, 300] = commands.Param(
        name="poll_time", description="Insert a number between 10 and 300."
    ),
) -> Thread:
    if (
        "movie" not in command.channel.name.lower()
        and command.channel.type != "text"
    ):
        return await command.response.send_message(
            "Looks like you're on the wrong channel.",
            delete_after=DELETE_AFTER,
        )

    movies: list[str] = movies.split(", ")
    movies: list[str] = [movie.replace(":", "") for movie in movies]

    match movies:
        case _ if len(movies) <= 1:
            return await command.response.send_message(
                "Too few arguments.", delete_after=DELETE_AFTER
            )

        case _ if len(movies) > 5:
            return await command.response.send_message(
                "Too many arguments.", delete_after=DELETE_AFTER
            )

    await command.response.send_message(
        f"Starting a poll with: {', '.join(movies).title()}",
        delete_after=DELETE_AFTER,
    )

    thread: Thread = await command.channel.create_thread(
        name=f"{', '.join(movies).title()} Poll",
        auto_archive_duration=60,
        type=ChannelType.public_thread,
    )

    numbers: dict[int, str] = {
        1: "1\uFE0F\u20E3",
        2: "2\uFE0F\u20E3",
        3: "3\uFE0F\u20E3",
        4: "4\uFE0F\u20E3",
        5: "5\uFE0F\u20E3",
    }

    thread_messages: list[int] = []

    try:

        films: dict[str, str] | list[dict[str, str]] = movie_wrapper(
            Utils.clean_phrase(movies)
        )

    except HTTPError:
        await thread.send(f"Movie not found.")
        await sleep(DELETE_AFTER)
        return await thread.delete()

    for movie in enumerate(movies, start=1):
        embed_movie: Embed = Embed()
        embed_movie.color = Colour.blurple()
        embed_movie.title = "{} - {}: {}".format(
            numbers[movie[0]],
            films[movie[0] - 1]["type"].title(),
            films[movie[0] - 1]["title"],
        )
        embed_movie.set_thumbnail(url=films[movie[0] - 1]["poster"])
        embed_movie.description = films[movie[0] - 1]["description"]
        embed_movie.url = films[movie[0] - 1]["imdb_url"]
        embed_movie.set_footer(
            text=("Genres: {}\nYear: {}\nRating: {}/10 \U0001f31f").format(
                " | ".join(films[movie[0] - 1]["genres"]),
                films[movie[0] - 1]["created_at"],
                films[movie[0] - 1]["rating"],
            )
        )

        thread_message: Message = await thread.send(embed=embed_movie)
        thread_messages.append(thread_message.id)

    message: Message = await thread.send("Voting ...")
    for i in range(len(movies)):
        await message.add_reaction(numbers[i + 1])
    await sleep(float(poll_time))

    reactions: list[str] = []

    reactions_info: list[dict[str, str | int]] = []

    for reaction in bot.get_message(message.id).reactions:
        match reaction.me:
            case True:
                reaction_stats = {
                    "reaction": None,
                    "users": None,
                    "count": None,
                }

                reaction_stats["reaction"] = reaction.emoji

                users = []
                async for user in reaction.users():
                    users.append(user.name)
                    reactions.append(reaction.emoji)

                reaction_stats["users"] = users
                reaction_stats["count"] = reaction.count

                reactions_info.append(reaction_stats)

    winner: tuple[str, int] = Utils.frequently(reactions)[0]

    embed_winner: Embed = bot.get_message(
        thread_messages[int(winner[0].replace("\uFE0F\u20E3", "")) - 1]
    ).embeds[0]
    embed_winner.color = Colour.green()
    embed_winner.description = "Win with {} votes.".format(str(winner[1]))

    await message.channel.send(embed=embed_winner)

    await message.channel.edit(
        name=f"\U0001f6ab Locked | {thread.name}",
        locked=True,
        archived=True,
    )


@poll.error
async def pool_cooldown_error(
    ctx: ApplicationCommandInteraction,
    error: commands.errors.CommandOnCooldown,
) -> Message:
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.response.send_message(
            f"Command on cooldown, "
            f"{Utils.seconds_to_minutes(error.retry_after)} minutes remaning.",
            delete_after=DELETE_AFTER,
        )


@commands.cooldown(rate=2, per=60, type=commands.BucketType.user)
@bot.slash_command(name="suggestion", description="make a movie suggestion.")
async def suggestion(command, movie: str) -> Message:

    if (
        "movie" not in command.channel.name.lower()
        and command.channel.type != "text"
    ):
        return await command.response.send_message(
            "Looks like you're on the wrong channel.",
            delete_after=DELETE_AFTER,
        )

    await command.response.send_message(
        "Sending your suggestion.", delete_after=DELETE_AFTER
    )

    try:
        film: dict[str, str] = wrapper.movie_wrapper(
            normalize("NFD", movie).encode("ascii", "ignore").decode("utf8")
        )
    except HTTPError:
        return await command.channel.send(
            f"{movie} not found.", delete_after=DELETE_AFTER
        )

    embed_movie: Embed = Embed()
    embed_movie.color = Colour.yellow()
    embed_movie.title = "\u2139\uFE0F - {}: {}".format(
        film["type"].title(), film["title"]
    )
    embed_movie.set_thumbnail(url=film["poster"])
    embed_movie.description = film["description"]
    embed_movie.set_footer(
        text=(
            "Genres: {}\nDate: {}\nRating: {}/10 \U0001f31f"
            "\nSuggested by: {}"
        ).format(
            " | ".join(film["genres"]),
            film["created_at"],
            film["rating"],
            command.user.name,
        )
    )

    await command.channel.send(embed=embed_movie)


@suggestion.error
async def suggestion_cooldown_error(
    ctx: ApplicationCommandInteraction,
    error: commands.errors.CommandOnCooldown,
) -> Message:
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.response.send_message(
            f"Command on cooldown, "
            f"{Utils.seconds_to_minutes(error.retry_after)} minutes remaning.",
            delete_after=DELETE_AFTER,
        )

