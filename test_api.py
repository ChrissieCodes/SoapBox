import config
import requests
import pytest


def post_to_add_recommendation(itemID, uniqueUserMatchID, findItem, date):
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_recommendation", json={"itemID": itemID, "matchID": uniqueUserMatchID, "findItem": findItem, "date": date}
    )
    assert r.status_code == 201

@pytest.mark.usefixtures("in_memory_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch():
    post_to_add_recommendation("pizza","bettygeorge", "cheshirecat.com", "2011-01-02")
    post_to_add_recommendation("pizza","bettyjohn",  "misspiggys.com", "2011-01-01")
    post_to_add_recommendation("waffles","bettyphillip", "neverenough.com", "2015-01-01")
    data = {"itemID": "pizza", "matchID": "bettysue", "findItem":"whereisit.com"}

    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201


@pytest.mark.usefixtures("in_memroy_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    data = {"itmeID": "pizza", "matchID": "bettybelle", "findItem": "whereisit.com"}
    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid recommendation"
