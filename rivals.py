from enum import Enum


class Rival(Enum):
    """HUMAN = 1
    AIrandom = 2
    AIeasy = 3
    AInormal = 4
    ONLINE = 5"""
    AIeasy = 1
    AInormal = 2
    AIrandom = 3
    HUMAN = 4
    ONLINE = 5

    @staticmethod
    def sort_tuple(first, second):
        if first.value < second.value:
            return first, second
        return second, first
