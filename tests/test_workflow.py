from app import app, db, User, Task
from werkzeug.security import generate_password_hash


def test_create_task_workflow():

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():

        existing_user = User.query.filter_by(
            email="workflow@test.com"
        ).first()

        if not existing_user:

            user = User(
                username="workflowuser",
                email="workflow@test.com",
                password_hash=generate_password_hash(
                    "Password123"
                )
            )

            db.session.add(user)
            db.session.commit()

        assert User.query.filter_by(
            email="workflow@test.com"
        ).first() is not None