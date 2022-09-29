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

