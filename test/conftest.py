import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from pathlib import Path
import time
import requests
from soapbox.domain.recommendations import Recommendation
import config
# import flaskapi
from flask import Flask

from adapters.orm import metadata, start_mappers

@pytest.fixture(scope="session")
def sqllite_db():
    engine = create_engine(config.get_sqlite_file_url())
    metadata.create_all(engine)
    return engine
    
@pytest.fixture(scope="session")
def tables(engine):
    metadata.create_all(engine)
    try:
        yield
    finally:
        metadata.drop_all(engine)

@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    return engine

@pytest.fixture
def sqlite_session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def session(sqlite_session_factory):
    return sqlite_session_factory()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def restart_api():
    path=(Path(__file__).parent / "recommendations.db")
    path.touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()

@pytest.fixture
def add_ranking(session):
    recommendations_added = set()
    matches_added = set()


    def _add_lines(lines):
        for itemID, uniqueUserMatchID, findItem, date in lines:
            session.execute(
                "INSERT INTO recommendations (itemID, uniqueUserMatchID, findItem, date)"
                " VALUES (:itemID, :uniqueUserMatchID, :findItem, :date)",
                dict(itemID=itemID, uniqueUserMatchID=uniqueUserMatchID, findItem=findItem, date=date),
            )
            [[reference]] = session.execute(
                "SELECT findItem FROM recommendations WHERE uniqueUserMatchID=:uniqueUserMatchID AND itemID=:itemID",
                dict(uniqueUserMatchID=uniqueUserMatchID, itemID=itemID),
            )
            recommendations_added.add(reference)
            matches_added.add(uniqueUserMatchID)

        session.commit()

    yield _add_lines

    for item in recommendations_added:
        session.execute(
            "DELETE FROM recommendations WHERE itemID=:item",
            dict(itemId=item),
        )

    for item in matches_added:
        session.execute(
            "DELETE FROM items WHERE itemName=:item", dict(itemName=item),
        )
        session.commit()

    
