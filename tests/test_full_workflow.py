from app import app, User, Task

def test_full_workflow():

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    tester = app.test_client()

    tester.post(
        "/register",
        data={
            "username": "flowuser999",
            "email": "flow999@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    tester.post(
        "/login",
        data={
            "email": "flow999@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    response = tester.post(
        "/add",
        data={
            "task": "Pytest Workflow Task",
            "priority": "High",
            "category": "Work",
            "due_date": ""
        },
        follow_redirects=True
    )

    assert response.status_code == 200

    with app.app_context():

        task = Task.query.filter_by(
            content="Pytest Workflow Task"
        ).first()

        assert task is not None