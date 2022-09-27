from collections import Counter

class Utils:
    @staticmethod
    def frequently(freq: list[str],) -> tuple[str, int]:
        return Counter(freq).most_common(1)

    @staticmethod
    def seconds_to_minutes(time: float) -> float:
        return round(time / 60.0, 2)