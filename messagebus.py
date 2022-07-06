from typing import List, Dict, Callable, Type
# import email
import events


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


def recommendation_was_rated(event: events.RatedRecommendation):
    if event._recommendationRating==1:
        rating = "good"
    else:
        rating = "bad"
    email.send_mail(
        "betty@gmailfakeemail.com",
        f"{event.RequesterID}, thinks your suggestion of {event.item} at {event.findItem} was a {rating} idea",
    )


HANDLERS = {
    events.RatedRecommendation: [recommendation_was_rated],
}  # type: Dict[Type[events.Event], List[Callable]]
