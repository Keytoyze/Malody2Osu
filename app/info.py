class Comparable:

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        other_value = other.value if isinstance(other, Comparable) else other
        return self.value == other_value

    def __ne__(self, other):
        other_value = other.value if isinstance(other, Comparable) else other
        return self.value != other_value

    def __gt__(self, other):
        other_value = other.value if isinstance(other, Comparable) else other
        return self.value > other_value

    def __lt__(self, other):
        other_value = other.value if isinstance(other, Comparable) else other
        return self.value < other_value

    def __ge__(self, other):
        other_value = other.value if isinstance(other, Comparable) else other
        return self.value >= other_value

    def __le__(self, other):
        other_value = other.value if isinstance(other, Comparable) else other
        return self.value <= other_value
