from enum import IntEnum, auto

from dataclasses import dataclass


class Gender(IntEnum):
    MALE = auto()
    FEMALE = auto()
    ANYONE = auto()


class Age(IntEnum):
    LESS_18 = auto()
    FROM_18_TO_21 = auto()
    FROM_22_TO_25 = auto()
    MORE_25 = auto()


@dataclass
class SearchParams:
    my_gender: Gender
    companion_gender: Gender

    my_age: Age
    companion_age: Age
