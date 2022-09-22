from watchparty_bot.src import wrapper
from watchparty_bot.src.utils import Utils
from disnake.ext import commands
from disnake import Embed, ChannelType, Thread, Message, TextChannel, Colour
from asyncio import sleep
from unicodedata import normalize
from requests import HTTPError


bot: commands.Bot = commands.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} \U0001f4a1")


@bot.slash_command(name="poll", description="Make an poll.")
async def poll(command, movies: str) -> Thread:
    if (
        "movie" not in command.channel.name.lower()
        and command.channel.type != "text"
    ):
        return await command.response.send_message(
            "Looks like you're on the wrong channel."
        )

    movies: list[str] = movies.split(",")
    movies: list[str] = [movie.replace(":", "") for movie in movies]

    await command.response.send_message(
        f"Starting a poll with: {', '.join(movies).title()}"
    )

    thread: Thread = await command.channel.create_thread(
        name=f"{', '.join(movies).title()} Poll",
        auto_archive_duration=60,
        type=ChannelType.public_thread,
    )

    # TODO: make only poll with 5 options.
    numbers: dict[int, str] = {
        1: "1\uFE0F\u20E3",
        2: "2\uFE0F\u20E3",
        3: "3\uFE0F\u20E3",
        4: "4\uFE0F\u20E3",
        5: "5\uFE0F\u20E3",
    }

    thread_messages: list[int] = []

    for movie in enumerate(movies, start=1):
        try:
            film: dict[str, str] | list[
                dict[str, str]
            ] = wrapper.movie_wrapper(
                normalize("NFD", movie[1])
                .encode("ascii", "ignore")
                .decode("utf8")
            )
        except HTTPError:
            return await command.channel.send("Movie not found.")
        embed_movie: Embed = Embed()
        embed_movie.color = Colour.blurple()
        embed_movie.title = "{} - {}: {}".format(
            numbers[movie[0]], film["type"].title(), film["title"]
        )
        embed_movie.set_thumbnail(url=film["poster"])
        embed_movie.description = film["description"]
        embed_movie.set_footer(
            text="Genres: {}\nDate: {}\nRating: {}/10 \U0001f31f".format(
                " | ".join(film["genres"]), film["created_at"], film["rating"]
            )
        )

        thread_message: Message = await thread.send(embed=embed_movie)
        thread_messages.append(thread_message.id)

    message: Message = await thread.send("Voting ...")
    for i in range(len(movies)):
        await message.add_reaction(numbers[i + 1])
    await sleep(15)
    # TODO: Make an for to get each emoji (parameters of reactions is a string of emoji.)
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

    winner: tuple[str, int] = Utils.frequentily(reactions)[0]

    embed_winner: Embed = bot.get_message(
        thread_messages[int(winner[0].replace("\uFE0F\u20E3", "")) - 1]
    ).embeds[0]
    embed_winner.color = Colour.green()
    embed_winner.description = "Win with {} votes.".format(str(winner[1]))

    await message.channel.send(embed=embed_winner)
    # TODO: close thread.


@bot.slash_command(name="suggestion", description="make a movie suggestion.")
async def suggestion(command, movie: str) -> Message:

    # TODO: check if bot send message in movie channel.

    film: dict[str, str] | list[dict[str, str]] = wrapper.movie_wrapper(
        normalize("NFD", movie).encode("ascii", "ignore").decode("utf8")
    )

    embed_movie: Embed = Embed()
    embed_movie.color = Colour.yellow()
    embed_movie.title = "\u2139\uFE0F - {}: {}".format(
        film["type"].title(), film["title"]
    )
    embed_movie.set_thumbnail(url=film["poster"])
    embed_movie.description = film["description"]
    embed_movie.set_footer(
        text="Genres: {}\nDate: {}\nRating: {}/10 \U0001f31f".format(
            " | ".join(film["genres"]), film["created_at"], film["rating"]
        )
    )

    await command.channel.send(embed=embed_movie)


@bot.slash_command(
    name="clear", description="Clear 100 messages in Movie text chat."
)
async def clear(command) -> TextChannel:
    if (
        "movie" not in command.channel.name.lower()
        and command.channel.type != "text"
    ):
        return await command.response.send_message(
            "Looks like you're on the wrong channel."
        )

    await command.response.send_message(
        "This process may take a while and will only delete 100 messages."
    )
    count: int = 0

    async for _ in command.channel.history(limit=None):
        count += 1

    await command.channel.send("This channel has {} messages.".format(count))
    await command.channel.send(command.channel.type)

    sleep(15)

    await command.channel.purge()
