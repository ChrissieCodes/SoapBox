from __future__ import annotations
from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

import messagebus
import config
from soapbox.adapters import repository




class AbstractUnitOfWork(ABC):
    repo: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()
    
    def commit(self):
        self._commit()
        self.publish_events()

    def publish_events(self):
        for recommendation in self.repo.seen:
            while recommendation.events:
                event = recommendation.events.pop(0)
                messagebus.handle(event)

    @abstractmethod
    def commit(self):
        raise NotImplementedError


    @abstractmethod
    def rollback(self):
        raise NotImplementedError


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_sqlite_file_url(),
        isolation_level="SERIALIZABLE",
    )
)

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.repo = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()