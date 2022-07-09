from datetime import date
from typing import Optional
from dataclasses import dataclass


class Command:
    pass


@dataclass
class Rating(Command):
    reference: int
    rating: int


@dataclass
class Ranking(Command):
    uniqueUserMatchID: str
    rank : float


