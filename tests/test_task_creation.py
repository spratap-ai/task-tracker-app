from app import app

def test_home_requires_login():

    app.config["TESTING"] = True

    tester = app.test_client()

    response = tester.get("/")

    assert response.status_code == 302