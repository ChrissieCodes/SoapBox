from datetime import datetime, timezone
import pytest
from unitofwork import SqlAlchemyUnitOfWork
from conftest import sqlite_session_factory
# from services import setRating, setRank, uow_setRating, add_recommendation, add_userMatch, getRankedRecommendations, getRecommendersForItem
# from CookiesAndBeer.unitofwork import FakeUnitOfWork
from recommendations import Recommendation, MatchUsers, setRank, SameRecommendations, not_same_recommendation
import unitofwork



def insert_recommendation(session, itemID, uniqueUserMatchID, date, findItem, _recommendationRating = None, _rank = 0):
    session.execute(
        """
        INSERT INTO recommendations (date, uniqueUserMatchID, itemID, findItem, _recommendationRating, _rank)
        VALUES(:date,:uniqueUserMatchID,:itemID,:findItem,:_recommendationRating, :_rank)
        """,
            dict(
            date=date, 
            findItem=findItem,
            uniqueUserMatchID=uniqueUserMatchID,
            itemID=itemID,
            _recommendationRating=_recommendationRating,
            _rank=_rank,
        ),
    )

def insert_userMatch(session, RequesterID, RecommenderID):
    session.execute(
        """
        INSERT INTO match_users (reference, RequesterID, RecommenderID)
        VALUES(:reference,:RequesterID,:RecommenderID)
        """,
            dict(reference = RequesterID + RecommenderID,
            RequesterID=RequesterID, 
            RecommenderID=RecommenderID,
        ),
    )

def get_requester_from_usermatch(session, reference):
    [[requesterID]] = session.execute(
        'SELECT RequesterID FROM match_users WHERE reference=:reference',
        dict(reference=reference)
    )
    return requesterID


def get_rating(session, reference):
    [[recommendationrating]]=session.execute(
        'SELECT _recommendationRating FROM recommendations WHERE reference=:reference',
        dict(reference=reference),
    )
    return recommendationrating

def setRating(session,response):
    uow = SqlAlchemyUnitOfWork(sqlite_session_factory)
    nu: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    insert_recommendation(session, f"pizza", f"Betty-George", nu.isoformat(), f"http://example.com")
    uow.commit()
    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with uow:
        rec = uow.repo.get(0)
        rec.setRating(response)

#this is messed up because i need to persist the rank for the user match instad of the recommendation. The rank doesn't change for every recommendation so it should not be given more reasons to change than it needs
# def get_ranking(session, uniqueUserMatchID):
#     [[recommendationrating]]=session.execute(
#         'SELECT _recommendationRating FROM recommendations WHERE uniqueUserMatchID=:uniqueUserMatchID',
#         dict(uniqueUserMatchID=uniqueUserMatchID),
#     )
#     return recommendationrating

def get_recommendation(session, reference):
    [[itemID, findItem, uniqueUserMatchID]] = session.execute(
        "SELECT itemID, findItem, uniqueUserMatchID FROM recommendations WHERE reference=:reference",
        dict(reference=reference)
    )
    return itemID, findItem, uniqueUserMatchID

def test_can_retrieve_recommendation(sqlite_session_factory):
    session = sqlite_session_factory()
    nu: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    insert_recommendation(session, f"pizza", f"Betty-George", nu.isoformat(), f"http://example.com")
    session.commit()

    recommendation: Recommendation = None
    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)

    with uow: 
        recommendation = uow.repo.list_recommendations()[0]
        assert recommendation.itemID=="pizza"

def test_can_retrieve_userMatch(sqlite_session_factory):
    session = sqlite_session_factory()
    insert_userMatch(session, f"Betty", f"George")
    session.commit()

    matches: MatchUsers = None
    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)

    with uow: 
        match = uow.repo.list_matches()[0]
        print(match.reference)
        assert match.reference=="BettyGeorge"


def test_set_ranking_for_usermatch(sqlite_session_factory):
    session = sqlite_session_factory()
    nu: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    insert_userMatch(session,"betty","george")
    insert_userMatch(session, "betty","john")
    insert_recommendation(session, f"pizza",f"bettygeorge", nu.isoformat() ,f"getpizza.com", _recommendationRating=1) #because we have a passing set rating test() &we assume data has already been set
    insert_recommendation(session,f"icecream",f"bettygeorge", nu.isoformat(), f"geticecream.com",_recommendationRating=0)
    insert_recommendation(session,f"jello",f"bettygeorge", nu.isoformat(), f"getjello.com",  _recommendationRating=0)
    insert_recommendation(session, f"beer",f"bettyjohn", nu.isoformat(), f"getbeer.com",_recommendationRating=0)
    session.commit()

    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)

    with uow:
        match = uow.repo.select_for_update_match(reference="bettygeorge")
        recs = uow.repo.list_rated_recommendations()
        rank = setRank(recs,"bettygeorge")
        match.setRank(rank,"bettygeorge")
        uow.commit()
        rank_sql = uow.repo.get_match(reference="bettygeorge")
        assert rank_sql._rank == 1/3
        


def test_uow_can_retrieve_a_user_match_from_recommendation_(sqlite_session_factory):
    session = sqlite_session_factory()
    nu: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    nu2: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    insert_recommendation(session, f"pizza", f"Betty-George", nu.isoformat(), f"http://example.com")
    insert_recommendation(session, f"pizza", f"Betty-John", nu2.isoformat(), f"http://examplepizza.com")    
    session.commit()
    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with uow:
        recommendation = uow.repo.list_recommendations()
        for rec in recommendation:
            if rec.reference==2:
                rec_user = rec.uniqueUserMatchID

    assert rec_user == "Betty-John"

def test_select_for_update(sqlite_session_factory):
    session = sqlite_session_factory()
    nu: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    nu2: datetime = datetime(2022, 4, 25, 0,0, 0, 0, tzinfo=timezone.utc)
    insert_recommendation(session, f"pizza", f"Betty-George", nu.isoformat(), f"http://example.com")
    insert_recommendation(session, f"pizza", f"Betty-John", nu2.isoformat(), f"http://examplepizza.com")
    session.commit()

    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)

    with uow:
        retrieved = uow.repo.select_for_update(reference=1)
        retrieved.setRating("bad")
        uow.commit()
    rate = get_rating(session, 1)
    assert rate==0


def test_return_list_by_rank(sqlite_session_factory):
    session = sqlite_session_factory()
    nu: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    nu2: datetime = datetime(2022, 4, 25, 0,0, 0, 0, tzinfo=timezone.utc)
    nu3: datetime = datetime(2022, 4, 26, 0,0, 0, 0, tzinfo=timezone.utc)
    nu4: datetime = datetime(2022, 4, 27, 0,0, 0, 0, tzinfo=timezone.utc)
    insert_userMatch(session,"betty","george")
    insert_userMatch(session,"betty","john")
    insert_recommendation(session, f"ice cream", f"bettygeorge", nu.isoformat(), f"http://example.com")
    insert_recommendation(session, f"pizza", f"bettygeorge", nu2.isoformat(), f"http://examplepizza.com")
    insert_recommendation(session, f"cookies", f"bettygeorge", nu2.isoformat(), f"http://examplepizza.com")
    insert_recommendation(session, f"ice cream", f"bettyjohn", nu3.isoformat(), f"http://examplepizza.com")
    insert_recommendation(session, f"beer", f"bettyjohn", nu4.isoformat(), f"http://examplepizza.com")
    session.commit()

    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)

    with uow:
        retrieved = uow.repo.list_recommendations()
        retrieved[1].setRating("good")
        retrieved[2].setRating("bad")
        retrieved[4].setRating("bad")
        rated = uow.repo.list_rated_recommendations()
        rank = setRank(retrieved,"bettygeorge")
        rate_George = uow.repo.select_for_update_match(reference="bettygeorge")
        rate_George.setRank(rank,rate_George.reference)
        rank2 = setRank(retrieved,"bettyjohn")
        rate_John = uow.repo.select_for_update_match(reference="bettyjohn")
        rate_John.setRank(rank2,rate_John.reference)
        uow.commit()
        ranked_recommenders = uow.repo.list_ordered_ranked_recommendations("ice cream")
        expected = [get_recommendation(session, 1),get_recommendation(session, 4)]
        assert ranked_recommenders==expected

def test_same_recommendation_raises_exception_and_rollsback(sqlite_session_factory):
    class MyException(Exception):
        pass
    session = sqlite_session_factory()
    nu: datetime = datetime(2022, 4, 24, 0,0, 0, 0, tzinfo=timezone.utc)
    insert_userMatch(session,"betty","george")
    insert_userMatch(session, "betty","john")
    insert_recommendation(session, f"beer",f"bettyjohn", nu.isoformat(), f"getbeer.com",_recommendationRating=0)
    session.commit()

    uow = unitofwork.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with pytest.raises(SameRecommendations):
        with uow:
            new_rec = Recommendation(f"bettyphillip", f"beer",f"getbeer.com",nu.isoformat())
            list_recs = uow.repo.list_recommendations()
            print(not_same_recommendation(new_rec,list_recs,new_rec.itemID))
            if not not_same_recommendation(new_rec,list_recs,new_rec.itemID):
                raise SameRecommendations()
    new_session = sqlite_session_factory()
    rows = list(new_session.execute('SELECT itemID, findItem, uniqueUserMatchID FROM recommendations'))
    assert rows == [get_recommendation(session,1)]
