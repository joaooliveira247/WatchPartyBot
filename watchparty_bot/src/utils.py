from collections import Counter
from unicodedata import normalize
from datetime import timedelta


class Utils:
    @staticmethod
    def frequently(
        freq: list[str],
    ) -> tuple[str, int]:
        return Counter(freq).most_common(1)

    @staticmethod
    def seconds_to_minutes(time: float) -> str:
        return str(timedelta(seconds=time))

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