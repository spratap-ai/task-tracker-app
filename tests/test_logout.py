from app import app


def test_logout():

    tester = app.test_client()

    tester.post(
        "/register",
        data={
            "username": "logoutuser",
            "email": "logout@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    tester.post(
        "/login",
        data={
            "email": "logout@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    response = tester.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200