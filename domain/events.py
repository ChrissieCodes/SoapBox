#even for email notification when someone adds a recommendation
#TODO: 1.create an trigger when someone makes a recommendations 2. Each time a recommendation is made from a different user the recommendations get added to the list in order 2.User(Requester) takes the recommendation and ranks it 3. When a recommendation is ranked, the notification (messagebus) of the ranking goes to the User(Recommender)

from dataclasses import dataclass


class Event:
    pass


    

@dataclass
class RatedRecommendation(Event):
    findItem : str
    item : str
    _recommendationRating : int

