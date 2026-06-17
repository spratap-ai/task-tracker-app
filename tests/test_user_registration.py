from app import app

def test_register_submit():

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    tester = app.test_client()

    response = tester.post(
        "/register",
        data={
            "username": "pytestuser123",
            "email": "pytest123@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    assert response.status_code == 200