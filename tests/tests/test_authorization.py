#users cannot access another user's task.
from app import app


def test_user_cannot_access_other_user_task():

    tester = app.test_client()

    # User 1
    tester.post(
        "/register",
        data={
            "username": "user1",
            "email": "user1@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    tester.post(
        "/login",
        data={
            "email": "user1@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    tester.post(
        "/add",
        data={
            "task": "Secret Task",
            "priority": "High",
            "category": "Work"
        },
        follow_redirects=True
    )

    tester.get("/logout", follow_redirects=True)

    # User 2
    tester.post(
        "/register",
        data={
            "username": "user2",
            "email": "user2@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    tester.post(
        "/login",
        data={
            "email": "user2@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    response = tester.get(
        "/edit/1",
        follow_redirects=True
    )

    assert response.status_code == 404