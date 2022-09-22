from requests import post, Response, HTTPError

# TODO: make this function recursive
def movie_wrapper(
    movies: str | list[str],
) -> dict[str, str | float] | list[dict[str, str | float]]:

    headers: dict[str] = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    if isinstance(movies, str):

        response: Response = post(
            "https://i-m-d-b.herokuapp.com/",
            data="tt={}".format(movies.replace(" ", "%20")),
            headers=headers,
        )

        try:
            response = response.json()["1"]
            genres: list[str] = [
                genre.replace("#", "") for genre in response["genres"]
            ]
            # genres = [x + " | " for x in genres]
            movie_cleaned: dict[str, str] = {
                "title": response["jsonnnob"]["name"],
                "type": response["jsonnnob"]["@type"],
                "genres": genres,
                "created_at": response["jsonnnob"]["datePublished"],
                "rating": response["jsonnnob"]["aggregateRating"][
                    "ratingValue"
                ],
                "poster": response["jsonnnob"]["image"],
                "description": response["jsonnnob"]["description"],
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
