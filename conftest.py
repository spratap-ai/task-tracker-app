import os
from dotenv import load_dotenv

load_dotenv(".env.test", override=True)
os.environ["PYTEST_RUNNING"] = "true"

from app import app, db

print(">>> FINAL DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])

def pytest_configure():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

def pytest_sessionstart(session):
    with app.app_context():
        db.create_all()