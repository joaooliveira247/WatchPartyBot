from requests import post, Response, HTTPError

def movie_wrapper(
    movies: str | list[str],
) -> dict[str, str | float] | list[dict[str, str | float]]:

    headers: dict[str, str] = {
        "user-agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36"
        )
    }

    if isinstance(movies, str):

        response: Response = post(
            "https://search.imdbot.workers.dev/",
            params={"q": movies.replace(" ", "%20")},
            headers=headers,
        )

        try:
            response = response.json()["description"][0]
            movie_cleaned: dict[str, str] = {
                "title": response["#TITLE"],
                "type": response["#IMDb_TITLE_TYPE"],
                "genres": response["#GENRE"],
                "created_at": response["#YEAR"],
                "rating": response["#RATING"]["#ONLYRATING"],
                "poster": response["#IMG_POSTER"],
                "description": response["#IMDb_SHORT_DESC"],
                "imdb_url": response["#IMDB_URL"],
            }

            return movie_cleaned
        except TypeError:
            # This treatment is being used because the API only returns status code 200
            raise HTTPError("Movie not found.")
        except KeyError:
            raise HTTPError("Movie not found.")

    movies_cleaned: list[dict[str, str | float]] = []
    for movie in movies:
        movies_cleaned.append(movie_wrapper(movie))

    return movies_cleaned