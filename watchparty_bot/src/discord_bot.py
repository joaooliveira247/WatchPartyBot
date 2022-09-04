from watchparty_bot.src import wrapper
from disnake.ext import commands
from disnake import Embed, ChannelType, Thread, Message
from asyncio import sleep
from unicodedata import normalize


bot: commands.Bot = commands.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user} \U0001f4a1")


@bot.slash_command(name="poll", description="Make an poll.")
async def thread(command, args: str) -> Thread:
    args: list[str] = args.split(",")
    args: list[str] = [x.replace(":", "") for x in args]

    thread: Thread = await command.channel.create_thread(
        name="This message will act as the thread's starting message.",
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

    for arg in enumerate(args, start=1):
        # TODO: maybe change api from wrapper.
        movie: dict[str, str] = wrapper.movie_wrapper(
            normalize("NFD", arg[1]).encode("ascii", "ignore").decode("utf8")
        )
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
    await message.channel.send(bot.get_message(message.id).reactions)
