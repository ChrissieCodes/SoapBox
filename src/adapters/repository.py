from abc import ABC, abstractmethod
import abc
from soapbox.domain.recommendations import MatchUsers, Recommendation
# import recommendations
from sqlalchemy import create_engine, desc

class AbstractRepository(ABC):
    def __init__(self):
        self.seen = set()

    @abc.abstractmethod
    def add(self, recommendation: Recommendation):
        self.seen.add(recommendation)
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Recommendation:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session
    
    def add(self, recommendation):
        self.session.add(recommendation)
        self.session.commit()
    
    def get(self,reference):
        return self.session.query(Recommendation).filter(Recommendation.reference==reference).one()

    def list_recommendations(self):
        return self.session.query(Recommendation).all()
    
    def list_rated_recommendations(self):
        return self.session.query(Recommendation).filter(Recommendation._recommendationRating!=None).all()
    
    def list_ordered_ranked_recommendations(self,item) -> MatchUsers:
        return self.session.query(Recommendation.itemID, Recommendation.findItem,Recommendation.uniqueUserMatchID).filter(Recommendation._recommendationRating==None).filter(Recommendation.itemID==item).order_by(desc(Recommendation._rank)).all()

    def select_for_update(self, reference) -> Recommendation:
        return self.session.query(Recommendation).filter(Recommendation.reference==reference).one()
    
    def filtered_item_list(self, itemID):
        return self.session.query(Recommendation).filter(Recommendation.itemID==itemID).all()

    def filtered_recommendation_list(self, uniqueUserMatch):
        return self.session.query(Recommendation).filter(Recommendation.uniqueUserMatchID==uniqueUserMatch).all()

    def add_match(self, match):
        self.session.add(match)
        self.session.commit()

    def get_match(self,reference):
        return self.session.query(MatchUsers).filter(MatchUsers.reference==reference).one()

    def list_matches(self):
        return self.session.query(MatchUsers).all()

    def select_for_update_match(self, reference) -> MatchUsers:
        return self.session.query(MatchUsers).filter(MatchUsers.reference==reference).one()

