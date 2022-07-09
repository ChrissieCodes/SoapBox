import recommendations
from datetime import date


def test_item_table_can_load_lines(session):
    session.execute(
        "INSERT INTO items (Name) VALUES "
        '("cookies"),'
        '("beer")'
    )
    expected = [
        recommendations.Item("cookies"),
        recommendations.Item("beer"),
    ]
    assert session.query(recommendations.Item).all() == expected


def test_user_table_can_load_lines(session):
    session.execute(
        "INSERT INTO users (userName) VALUES "
        '("EddieEats"),'
        '("DominicDrinks")'
    )
    expected = [
        recommendations.User("EddieEats"),
        recommendations.User("DominicDrinks"),
    ]
    assert session.query(recommendations.User).all() == expected


def test_retrieving_recommendations(session):
    session.execute(
        "INSERT INTO recommendations (date, uniqueUserMatchID, itemID, findItem) VALUES "
        '("2020-7-25", "Shell-Silver", "cookies", "www.findyouritem.com"),'
        '("2020-2-2", "Shell-Tina", "cookies", "www.findyourcookie.com")'
    )
    expected = [
        recommendations.Recommendation(
            "Shell-Silver", "cookies", "www.findyouritem.com", date=date(2020,7,25),reference=1),
        recommendations.Recommendation(
            "Shell-Tina", "cookies", "www.findyourcookie.com",date=date(2020,2,2),reference=2),
    ]
    assert session.query(recommendations.Recommendation).all() == expected

def test_saving_recommendations(session):
    recommendation = recommendations.Recommendation(
            "uniqueuserMatchID", "cookies", "url.com", date=date(2020,7,25))
    session.add(recommendation)
    session.commit()
    rows = session.execute(
        'SELECT uniqueUserMatchID, itemID, findItem, date, _recommendationRating FROM "recommendations"'
    )
    print(str(rows))
    assert list(rows)==[("uniqueuserMatchID", "cookies", "url.com","2020-07-25",None)]

