from recommendations import Recommendation, MatchUsers, User, Item
import events


# from sqlalchemy.orm import mapper, relationship
import pytest


def test_this_is_a_recommendation_with_correct_data_types():
    recommendation = Recommendation(
        "7-15-2022", "Jean-Joe", "cookies", "www.findyouritem.com")
    assert type(recommendation.date) == str
    assert type(recommendation.uniqueUserMatchID) == str
    assert type(recommendation.itemID) == str
    assert type(recommendation.findItem) == str


def test_this_is_a_recommendation_with_correct_data():
    recommendation = Recommendation(
        "Shell-Silver", "cookies", "www.findyouritem.com", "7-25-2020")
    assert recommendation.date == "7-25-2020"
    assert recommendation.uniqueUserMatchID == "Shell-Silver"
    assert recommendation.itemID == "cookies"
    assert recommendation.findItem == "www.findyouritem.com"
    assert isinstance(recommendation, Recommendation)


# def test_calculate_rank():
#     recommendationCount = 20
#     sumofratings = 15
#     score = Rank()
#     score.setRank(sumofratings, recommendationCount)
#     assert score._rank == 0.75
# refactored


def test_get_recommender_or_requester_user_id_from_recommendation():
    requestID = "ImaRequester"
    recommendID = "GinaeatsGarbagePlates"
    item = Item("coffee")
    matchID = MatchUsers(requestID, recommendID)
    recommendation = Recommendation(
        1, matchID.reference, item, "garbageinput.com", reference=1)
    recommender = matchID.getRecommender(matchID.reference)
    assert recommender == "GinaeatsGarbagePlates"
    requester = matchID.getRequester(matchID.reference)
    assert requester == "ImaRequester"


def test_get_user_from_input():
    user = User("BettyRec")
    assert isinstance(user, User)


def test_item_user_from_input():
    item = Item("Cookies")
    assert isinstance(item, Item)
    
def test_records_rating_event():
    recommendation = Recommendation(
        "Jean-Joe", "cookies", "www.findyouritem.com","7-15-2022")
    recommendation.setRating("bad")
    assert recommendation.events[-1] == events.RatedRecommendation(item="cookies",findItem="www.findyouritem.com",_recommendationRating = 0)

