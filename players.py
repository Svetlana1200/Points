from enum import Enum


class AI:
    def __ini__(self):
        pass


class AIrandom(AI):
    def __init__(self):
        self.name = "AIrandom"


class AIeasy(AI):
    def __init__(self):
        self.name = "AIeasy"


class AInormal(AI):
    def __init__(self):
        self.name = "AInormal"


class HUMAN:
    def __init__(self):
        self.name = "HUMAN"


class ONLINE:
    def __init__(self):
        self.name = "ONLINE"


def sort(first, second):
    if first.name < second.name:
        return first, second
    return second, first

