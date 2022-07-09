from conftest import sqlite_session_factory
from recommendations import *
from services import setRating, sumRatings, setRank, countRecommendationsForMatch,getRecommendersForItem, getRankedRecommendations, add_recommendation
from repository import AbstractRepository
from sqlalchemy import desc
import services
import unitofwork


#refactoring services for unit of work

class FakeRepository(AbstractRepository):
    def __init__(self,recommendations,matches):
        self._recommendations = set(recommendations)
        self._matches = set(matches)

    def add(self, recommendation):
        self._recommendations.add(recommendation)

    def get(self,itemID):
        return next(b for b in self._recommendations if b.itemID==itemID)

    def list_recommendations(self):
        return list(self._recommendations)
    
    def select_for_update(self, reference) -> Recommendation:
        return self.session.query(Recommendation).filter(reference==reference).with_for_update().one()

    def filtered_recommendation_list(self, uniqueUserMatch):
        return self.session.query(Recommendation).filter(Recommendation.uniqueUserMatchID==uniqueUserMatch).all()

    def add_match(self, match):
        self._matches.add(match)

    def get_match(self,reference):
        return next(b for b in self._match if b.reference==reference)

    def list_matches(self):
        return list(self._matches)
    
    def select_for_update_match(self, reference) -> MatchUsers:
        return self.session.query(MatchUsers).filter(reference==reference).with_for_update().one()

    def list_rated_recommendations(self):
        return self.session.query(Recommendation).filter(Recommendation._recommendationRating!=None).all()
    
    def list_ordered_ranked_recommendations(self) -> MatchUsers:
        return self.session.query(Recommendation).filter(Recommendation._recommendationRating!=None).order_by(desc(Recommendation._rank)).all()

class FakeUnitOfWork(unitofwork.AbstractUnitOfWork):
    def __init__(self):
        self.repo = FakeRepository([],[])
        self._committed = False

    def commit(self):
        self._committed = True

    def rollback(self):
        pass


def test_add_recommendation():
    uow = FakeUnitOfWork()
    services.add_recommendation("1234", "pizza", "getpizza.com", "7-12-1987",uow)
    uow.commit()
    assert uow.repo.list_recommendations() is not None

def test_add_User_Match():
    uow = FakeUnitOfWork()
    services.add_userMatch("Carol","Mark",uow)
    uow.commit()
    assert uow.repo.list_matches() is not None


    

def test_set_rating_on_particular_recommendation():
    recommendation1 = Recommendation("1234", "pizza", "getpizza.com", "7-12-1987", reference = 4)
    recommendation45 = Recommendation("1234", "icecream", "geticecream.com", "7-12-1997", reference = 45)
    rating=setRating("good", [recommendation1,recommendation45], 45)
    assert rating == 1
    assert recommendation45._recommendationRating==1
    rating2=setRating("bad", [recommendation1,recommendation45], 4)
    assert rating2 == 0
    assert recommendation1._recommendationRating==0


def test_calculate_recommendation_count_for_usermatch():
    item1 = Item("pizza")
    pizza = item1.Name
    item2 = Item('marshmallow')
    marshmallow = item2.Name
    mm = item2.Name
    requester1 = User("ImaRequester")
    requester2 = User("OtherRequester")
    recommender1 = User("AbbyEats")
    recommender2 = User("JoeHatesPizza")
    recommender3 = User("YinaEatsBeanas")
    recommender4 = User("MyNameSucks")
    recommender5 = User("AnOldUser")
    match1 = MatchUsers(requester1.userName, recommender1.userName)
    match2 = MatchUsers(requester1.userName, recommender2.userName)
    match4 = MatchUsers(requester1.userName, recommender4.userName)
    rec1 = Recommendation(match1.reference,
                          pizza, "garbageinput1.com", "7-16-2022", reference=1)
    rec2 = Recommendation(match2.reference,
                          marshmallow, "garbageinput2.com", "7-16-2022", reference=2)
    rec3 = Recommendation(match1.reference,
                          pizza, "garbageinput3.com", "7-16-2022", reference=3)
    rec4 = Recommendation(match4.reference,
                          pizza, "garbageinput4.com", "7-16-2022", reference=4)
    rec5 = Recommendation(match1.reference,
                          mm, "garbageinput5.com", "7-16-2022", reference=5)
    ratings = [rec1, rec2, rec3, rec4, rec5]
    setRating("good", ratings, 1)
    setRating("bad", ratings, 3)
    setRating("good", ratings, 5)
    count = countRecommendationsForMatch(ratings, match1.reference)
    assert count == 3


def test_calculate_recommendation_sum_for_usermatch():
    item1 = Item("pizza")
    pizza = item1.Name
    item2 = Item('marshmallow')
    marshmallow = item2.Name
    mm = item2.Name
    requester1 = User("ImaRequester")
    recommender1 = User("AbbyEats")
    recommender2 = User("JoeHatesPizza")
    recommender4 = User("MyNameSucks")
    match1 = MatchUsers(requester1.userName, recommender1.userName)
    match2 = MatchUsers(requester1.userName, recommender2.userName)
    match4 = MatchUsers(requester1.userName, recommender4.userName)
    rec1 = Recommendation(match1.reference,
                          pizza, "garbageinput1.com", "7-16-2022", reference=1)
    rec2 = Recommendation(match2.reference,
                          marshmallow, "garbageinput2.com", "7-16-2022", reference=2)
    rec3 = Recommendation(match1.reference,
                          pizza, "garbageinput3.com", "7-16-2022", reference=3)
    rec4 = Recommendation(match4.reference,
                          pizza, "garbageinput4.com", "7-16-2022", reference=4)
    rec5 = Recommendation(match1.reference,
                          mm, "garbageinput5.com", "7-16-2022", reference=5)
    ratings = [rec1, rec2, rec3, rec4, rec5]
    setRating("good", ratings, 1)
    setRating("bad", ratings, 3)
    setRating("good", ratings, 5)
    sum = sumRatings(ratings, match1.reference)
    assert sum == 2

def test_calculate_matchuser_ranking():
    item1 = Item("pizza")
    pizza = item1.Name
    item2 = Item('marshmallow')
    marshmallow = item2.Name
    mm = item2.Name
    requester1 = User("ImaRequester")
    requester2 = User("OtherRequester")
    recommender1 = User("AbbyEats")
    recommender2 = User("JoeHatesPizza")
    recommender3 = User("YinaEatsBeanas")
    recommender4 = User("MyNameSucks")
    recommender5 = User("AnOldUser")
    match1 = MatchUsers(requester1.userName, recommender1.userName)
    match2 = MatchUsers(requester1.userName, recommender2.userName)
    match4 = MatchUsers(requester1.userName, recommender4.userName)
    rec1 = Recommendation(match1.reference,
                        pizza, "garbageinput1.com", "7-16-2022", reference=1)
    rec2 = Recommendation(match2.reference,
                        marshmallow, "garbageinput2.com", "7-16-2022", reference=2)
    rec3 = Recommendation(match1.reference,
                        pizza, "garbageinput3.com", "7-16-2022", reference=3)
    rec4 = Recommendation(match4.reference,
                        pizza, "garbageinput4.com", "7-16-2022", reference=4)
    rec5 = Recommendation(match1.reference,
                        mm, "garbageinput5.com", "7-16-2022", reference=5)
    ratings = [rec1, rec2, rec3, rec4, rec5]
    setRating("good", ratings, 1)
    setRating("bad", ratings, 3)
    setRating("good", ratings, 5)
    rank = setRank(ratings, match1.reference)
    match1.setRank(rank,match1.reference)
    assert match1._rank == 2/3

def test_list_recommender_users():
    """
    if a bunch of people send a recommendation, list them, by their UserIDs
    """
    item1 = Item("pizza")
    pizza = item1.Name
    item2 = Item('marshmallow')
    mm = item2.Name
    requester1 = User("ImaRequester")
    requester2 = User("OtherRequester")
    recommender1 = User("AbbyEats")
    recommender2 = User("JoeHatesPizza")
    recommender3 = User("YinaEatsBeanas")
    recommender4 = User("MyNameSucks")
    recommender5 = User("AnOldUser")
    match1 = MatchUsers(requester1.userName, recommender1.userName)
    match2 = MatchUsers(requester1.userName, recommender2.userName)
    match3 = MatchUsers(requester2.userName, recommender3.userName)
    match4 = MatchUsers(requester1.userName, recommender4.userName)
    match5 = MatchUsers(requester1.userName, recommender5.userName)
    rec1 = Recommendation(match1.reference,
                          pizza, "garbageinput1.com", "7-16-2022", reference=1)
    rec2 = Recommendation(match2.reference,
                          pizza, "garbageinput2.com", "7-16-2022", reference=2)
    rec3 = Recommendation(match3.reference,
                          pizza, "garbageinput3.com", "7-16-2022", reference=3)
    rec4 = Recommendation(match4.reference,
                          pizza, "garbageinput4.com", "7-16-2022", reference=4)
    rec5 = Recommendation(match5.reference,
                          mm, "garbageinput5.com", "7-16-2022", reference=5)
    recommendations = [rec1, rec2, rec3, rec4, rec5]
    matches = [match1, match2, match3, match4, match5]
    itemRecs=getRecommendersForItem(
        recommendations, matches, pizza)
    assert itemRecs == {
        "AbbyEats", "JoeHatesPizza", "YinaEatsBeanas", "MyNameSucks"}

def test_list_recommender_users():
    """
    if a bunch of people send a recommendation, list them, by their rank
    """
    item1 = Item("pizza")
    pizza = item1.Name
    item2 = Item('marshmallow')
    mm = item2.Name
    requester1 = User("ImaRequester")
    requester2 = User("OtherRequester")
    recommender1 = User("AbbyEats")
    recommender2 = User("JoeHatesPizza")
    recommender3 = User("YinaEatsBeanas")
    recommender4 = User("MyNameSucks")
    recommender5 = User("AnOldUser")
    match1 = MatchUsers(requester1.userName, recommender1.userName)
    match2 = MatchUsers(requester1.userName, recommender2.userName)
    match3 = MatchUsers(requester2.userName, recommender3.userName)
    match4 = MatchUsers(requester1.userName, recommender4.userName)
    match5 = MatchUsers(requester1.userName, recommender5.userName)
    rec1 = Recommendation(match1.reference,
                          pizza, "garbageinput1.com", "7-16-2022", reference=1)
    rec2 = Recommendation(match2.reference,
                          pizza, "garbageinput2.com", "7-16-2022", reference=2)
    rec3 = Recommendation(match3.reference,
                          pizza, "garbageinput3.com", "7-16-2022", reference=3)
    rec4 = Recommendation(match4.reference,
                          pizza, "garbageinput4.com", "7-16-2022", reference=4)
    rec5 = Recommendation(match5.reference,
                          mm, "garbageinput5.com", "7-16-2022", reference=5)
    recommendations = [rec1, rec2, rec3, rec4, rec5]
    matches = [match1, match2, match3, match4, match5]
    listRecommenders = getRecommendersForItem(
        recommendations, matches, pizza)
    assert listRecommenders == {
        "AbbyEats", "JoeHatesPizza", "YinaEatsBeanas", "MyNameSucks"}


def test_order_recommender_list_by_Rank():
    """
    TODO:refactor to set this as a data set for all tests and call
    the complexity of the test is due to the calculation of the rank which needs more than one recommendation
    the factory pattern design patterns gang of four "factory boy package"
    """
    item1 = Item("pizza")
    item2 = Item("marshmallows")
    requester1 = User("ImaRequester")
    requester2 = User("OtherRequester")
    recommender1 = User("AbbyEats")
    recommender2 = User("JoeHatesPizza")
    recommender3 = User("YinaEatsBeanas")
    recommender4 = User("MyNameSucks")
    recommender5 = User("AnOldUser")
    match1 = MatchUsers(requester1.userName, recommender1.userName)
    match2 = MatchUsers(requester1.userName, recommender2.userName)
    match3 = MatchUsers(requester2.userName, recommender3.userName)
    match4 = MatchUsers(requester1.userName, recommender4.userName)
    match5 = MatchUsers(requester1.userName, recommender5.userName)
    rec1 = Recommendation(match1.reference,
                          item1.Name, "placetogetpizza.com", "8-2-2022", reference=1)
    match1._rank = 0.5
    rec2 = Recommendation(match2.reference, item1.Name,
                          "yourmom.com", "7-25-2020", reference=2)
    match2._rank = 0.4
    rec3 = Recommendation(match3.reference, item1.Name,
                          "mymom.com", "7-25-2020", reference=3)
    match3._rank = 0.77
    rec4 = Recommendation(match4.reference,
                          item1.Name, "homemade.com", "7-25-2020", reference=4)
    match4._rank = 0.25
    rec5 = Recommendation(match5.reference,
                          item2.Name, "notpizza.com", "7-25-2020", reference=5)
    match5._rank = 0
    recommenders = [
        recommender1,
        recommender2,
        recommender3,
        recommender4,
        recommender5,
    ]
    recommendations = [rec1, rec2, rec3, rec4, rec5]
    matches = [match1, match2, match3, match4, match5]
    ranked_recs = getRankedRecommendations(
        recommenders, recommendations, matches, item1.Name, requester1.userName)
    assert ranked_recs == [
        ["AbbyEats", 'pizza', "placetogetpizza.com"],
        ["JoeHatesPizza", 'pizza', "yourmom.com"],
        ["MyNameSucks", 'pizza', "homemade.com"],
    ]
