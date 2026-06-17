from app import app, Task
from app import app


def test_edit_task():

    tester = app.test_client()

    # Register user
    tester.post(
        "/register",
        data={
            "username": "edituser",
            "email": "edit@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    # Login
    tester.post(
        "/login",
        data={
            "email": "edit@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    # Create task
    tester.post(
        "/add",
        data={
            "task": "Original Task",
            "priority": "High",
            "category": "Work"
        },
        follow_redirects=True
    )
    with app.app_context():

        task = Task.query.filter_by(
            content="Original Task"
        ).first()

    task_id = task.id   

    # Edit first task
    response = tester.post(
        f"/edit/{task_id}",
        data={
            "task": "Updated Task",
            "priority": "Medium",
            "category": "Personal"
        },
        follow_redirects=True
    )

    assert response.status_code == 200