import config
import requests
import pytest


def post_to_add_recommendation(itemID, uniqueUserMatchID, findItem, date):
    url = config.get_api_url()
    print(url)
    # url localhost:5000
    r = requests.post(
        f"{url}/submit_recommendation", json={"itemID": itemID, "matchID": uniqueUserMatchID, "findItem": findItem, "date": date}
    )
    # localhost:5000/submit_recommendations
    assert r.status_code == 201

# @pytest.mark.usefixtures("in_memory_db") #creates sqlite engine
@pytest.mark.usefixtures("restart_api") #restarts the api
@pytest.mark.usefixtures("sqllite_db") #creates sqlite engine
def test_happy_path_returns_201_and_recommendation():
    post_to_add_recommendation("pizza","bettygeorge", "cheshirecat.com", "2011-01-02")
    post_to_add_recommendation("pizza","bettyjohn",  "misspiggys.com", "2011-01-01")
    post_to_add_recommendation("waffles","bettyphillip", "neverenough.com", "2015-01-01")
    data = {"itemID": "pizza", "matchID": "bettysue", "findItem":"whereisit.com","date":"2020-07-08"}
    url = config.get_api_url()
    print(url)
    r = requests.post(f"{url}/submit_recommendation", json=data)
    print(r)

    assert r.status_code == 201


@pytest.mark.skip(reason ="not implemented")
# @pytest.mark.usefixtures("in_memory_db")
@pytest.mark.usefixtures("restart_api")
@pytest.mark.usefixtures("sqllite_db")
def test_unhappy_path_returns_400_and_error_message():
    data = {"itemID": "pizza", "matchID": "bettybelle", "findItem": "whereisit.com","date":"2020-07-08"}
    url = config.get_api_url()
    r = requests.post(f"{url}/submit_recommendation", json=data)
    assert r.status_code == 404
    assert r.json()["message"] == f"Invalid recommendation"



# @pytest.mark.usefixtures("in_memory_db")
# @pytest.mark.usefixtures("restart_api")
# def test_happy_path_returns_201():
#     data = {"itemID": "pizza", "matchID": "bettysue", "findItem":"whereisit.com"}
#     url = config.get_api_url()
#     print(url)
#     r = requests.post(f"{url}/submit_recommendation", json=data)
#     print(r)

#     assert r.status_code == 201
