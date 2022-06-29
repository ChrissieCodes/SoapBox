#even for email notification when someone adds a recommendation

from dataclasses import dataclass


class Event:
    pass


@dataclass
class RatedRecommendation(Event):
    findItem : str
    item : str
    _recommendationRating : int
