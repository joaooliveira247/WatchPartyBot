from watchparty_bot.src import wrapper
from disnake.ext import commands
from disnake import Embed, ChannelType, Thread, Message, TextChannel
from asyncio import sleep
from unicodedata import normalize
from requests import HTTPError


bot: commands.Bot = commands.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} \U0001f4a1")


@bot.slash_command(name="poll", description="Make an poll.")
async def thread(command, args: str) -> Thread:
    if (
        "movie" not in command.channel.name.lower()
        | command.channel.type != "text"
    ):
        return await command.response.send_message(
            "Looks like you're on the wrong channel."
        )

    args: list[str] = args.split(",")
    args: list[str] = [x.replace(":", "") for x in args]

    # inter.response.send_message
    await command.response.send_message(
        f"Starting a poll with: {''.join(args).replace(' ', ', ').title()}"
    )

    thread: Thread = await command.channel.create_thread(
        name=f"{''.join(args).replace(' ', ', ').title()} Poll",
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

    for arg in enumerate(args, start=1):
        try:
            movie: dict[str, str] | list[
                dict[str, str]
            ] = wrapper.movie_wrapper(
                normalize("NFD", arg[1])
                .encode("ascii", "ignore")
                .decode("utf8")
            )
        except HTTPError:
            return await command.channel.send("Movie not found.")
        embed_movie: Embed = Embed()
        embed_movie.title = "{} - {}: {}".format(
            numbers[arg[0]], movie["type"].title(), movie["title"]
        )
        embed_movie.set_thumbnail(url=movie["poster"])
        embed_movie.description = movie["description"]
        embed_movie.set_footer(
            text="Genres: {}\nDate: {}\nRating: {}/10 \U0001f31f".format(
                "".join(movie["genres"]), movie["created_at"], movie["rating"]
            )
        )

        await thread.send(embed=embed_movie)

    message: Message = await thread.send("Voting ...")
    for i in range(len(args)):
        await message.add_reaction(numbers[i + 1])
    await sleep(15)
    # TODO: Make an for to get each emoji (parameters of reactions is a string of emoji.)
    reactions: list[dict[str, str | int]] = []

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

                reaction_stats["users"] = users
                reaction_stats["count"] = reaction.count

                reactions.append(reaction_stats)

    await message.channel.send(reactions)

@bot.slash_command(
    name="clear", description="Clear 100 messages in Movie text chat"
)
async def clear(command) -> TextChannel:
    if (
        "movie" not in command.channel.name.lower()
        | command.channel.type != "text"
    ):
        return await command.response.send_message(
            "Looks like you're on the wrong channel."
        )

    await command.response.send_message(
        "This process may take a while and will only delete 100 messages"
    )
    count: int = 0

    async for _ in command.channel.history(limit=None):
        count += 1

    await command.channel.send("This channel has {} messages".format(count))
    await command.channel.send(command.channel.type)

    sleep(15)

    await command.channel.purge()
