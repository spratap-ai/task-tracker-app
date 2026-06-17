#unauthenticated user cannot access the Profile page
from app import app


from app import app


def test_profile_requires_login():

    tester = app.test_client()

    response = tester.get(
        "/profile",
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"Email" in response.data

def test_change_password_requires_login():

    tester = app.test_client()

    response = tester.get(
        "/change-password",
        follow_redirects=True
    )

    assert response.status_code == 200

    assert b"Email" in response.data