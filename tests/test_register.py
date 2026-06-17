from app import app

def test_register_page():

    tester = app.test_client()

    response = tester.get("/register")

    assert response.status_code == 200

    assert b"Username" in response.data

    assert b"Email" in response.data

    assert b"Password" in response.data