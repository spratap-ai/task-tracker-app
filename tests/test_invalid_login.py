from app import app


def test_invalid_login():

    tester = app.test_client()

    response = tester.post(
        "/login",
        data={
            "email": "wrong@test.com",
            "password": "WrongPassword"
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"Invalid email or password" in response.data