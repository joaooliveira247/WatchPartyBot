from collections import Counter

class Utils:
    @staticmethod
    def frequently(freq: list[str],) -> tuple[str, int]:
        return Counter(freq).most_common(1)