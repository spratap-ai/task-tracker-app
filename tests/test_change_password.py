from app import app


def test_change_password_page():

    tester = app.test_client()

    response = tester.get(
        "/change-password",
        follow_redirects=True
    )

    assert response.status_code == 200


