from app import app, Task

def test_delete_task():

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    tester = app.test_client()

    # Register
    tester.post(
        "/register",
        data={
            "username": "deleteuser999",
            "email": "delete999@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    # Login
    tester.post(
        "/login",
        data={
            "email": "delete999@test.com",
            "password": "Password123"
        },
        follow_redirects=True
    )

    # Create task
    tester.post(
        "/add",
        data={
            "task": "Task To Delete",
            "priority": "High",
            "category": "Work",
            "due_date": ""
        },
        follow_redirects=True
    )

    # Find task ID
    with app.app_context():

        task = Task.query.filter_by(
            content="Task To Delete"
        ).first()

        task_id = task.id

    # Delete task
    response = tester.get(
        f"/delete/{task_id}",
        follow_redirects=True
    )

    assert response.status_code == 200

    # Verify deletion
    with app.app_context():

        deleted_task = Task.query.filter_by(
            content="Task To Delete"
        ).first()

        assert deleted_task is None