from requests import post, Response
from pprint import pprint

#TODO: make this function recursive
def movie_wrapper(movies: str | list[str]) -> dict[str, str] | list[dict[str, str]]:

    headers: dict[str] = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response: Response = post(
        "https://i-m-d-b.herokuapp.com/",
        data="tt={}".format(movies.replace(" ", "%20")),
        headers=headers,
    )

    match response.status_code:
        case 200:
            response = response.json()["1"]
            genres: list[str] = [genre.replace("#", "") for genre in response["genres"]]
            genres = [x + " | " for x in genres]
            movie: dict[str, str] = {
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

            return movie

        case 404:
            raise Exception("404 foda-se")

        case _:
            raise Exception("outro status code  foda se")
