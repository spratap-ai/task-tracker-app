from app import app

def test_login_page():

    tester = app.test_client()

    response = tester.get("/login")

    assert response.status_code == 200

    assert b"Email" in response.data

    assert b"Password" in response.data