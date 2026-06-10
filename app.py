from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user
)
from flask import Flask, request, redirect, render_template
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_login import UserMixin
import os
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get(
    "SECRET_KEY"
)
app.logger.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Read database connection string from environment variable
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# Database Tables

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Pending")
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default="Medium")
    category = db.Column(db.String(50), default="Work")

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

# REGISTER ROUTE
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect('/')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')

        password = request.form.get('password')

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            return redirect('/')

        return "Invalid Credentials"

    return render_template(
        'login.html'
 
   )

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/login')

# Home Page
@app.route('/')
@login_required
def home():

    search = request.args.get('search')
    priority_filter = request.args.get('priority_filter')
    status_filter = request.args.get('status_filter')
    category_filter = request.args.get('category_filter')

    query = Task.query.filter_by(
    user_id=current_user.id
    )

    if search:
        query = query.filter(
            Task.content.ilike(f"%{search}%")
        )

    if priority_filter:
        query = query.filter(
            Task.priority == priority_filter
        )
    if status_filter:
        query = query.filter(
            Task.status == status_filter
        )
    if category_filter:
        query = query.filter(
        Task.category == category_filter
        )   

    tasks = query.order_by(
        Task.due_date.asc()
    ).all()

    total_tasks = len(tasks)

    pending_tasks = len(
        [task for task in tasks if task.status == "Pending"]
    )

    completed_tasks = len(
        [task for task in tasks if task.status == "Completed"]
    )

    work_tasks = len(
    [task for task in tasks if task.category == "Work"]
    )

    personal_tasks = len(
    [task for task in tasks if task.category == "Personal"]
    )

    learning_tasks = len(
    [task for task in tasks if task.category == "Learning"]
    )

    finance_tasks = len(
    [task for task in tasks if task.category == "Finance"]
    )

    today = date.today()

    high_priority_tasks = len(
    [
        task for task in tasks
        if task.priority == "High"
    ]
    )

    overdue_tasks = len(
    [
        task for task in tasks
        if task.due_date
        and task.due_date < today
        and task.status != "Completed"
    ]
    )

    due_today_tasks = len(
    [
        task for task in tasks
        if task.due_date == today
        and task.status != "Completed"
    ]
   )

    completion_rate = (
    round(
        completed_tasks / total_tasks * 100
    )
    if total_tasks > 0
    else 0
   )

    return render_template(
    "index.html",
    tasks=tasks,
    total_tasks=total_tasks,
    pending_tasks=pending_tasks,
    completed_tasks=completed_tasks,
    work_tasks=work_tasks,
    personal_tasks=personal_tasks,
    learning_tasks=learning_tasks,
    finance_tasks=finance_tasks,

    high_priority_tasks=high_priority_tasks,
    overdue_tasks=overdue_tasks,
    due_today_tasks=due_today_tasks,
    completion_rate=completion_rate,

    today=today
      
  )
# Add Task
@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task_content = request.form.get('task')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority')
    category = request.form.get('category')

    if task_content:
        new_task = Task(
    content=task_content,
    due_date=datetime.strptime(
        due_date,
        "%Y-%m-%d"
    ).date() if due_date else None,
    priority=priority,
    category=category,
    user_id=current_user.id
    ) 
        db.session.add(new_task)
        db.session.commit()
        app.logger.info(
            f"Task created: {task_content}"
   )

    return redirect('/')

@app.route('/complete/<int:id>')
@login_required
def complete_task(id):

    task = Task.query.get_or_404(id)

    task.status = "Completed"

    db.session.commit()
    app.logger.info(
        f"Task completed: {task.content}"
    )

    return redirect('/')

# Delete Task
@app.route('/delete/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    app.logger.info(
        f"Task deleted: {task.content}"
    )
    db.session.delete(task)
    db.session.commit()

    return redirect('/')

#Edit Task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):

    task = Task.query.get_or_404(id)

    if request.method == 'POST':

        task.content = request.form.get('task')

        due_date = request.form.get('due_date')

        task.due_date = (
            datetime.strptime(
                due_date,
                "%Y-%m-%d"
            ).date()
            if due_date else None
        )

        task.priority = request.form.get('priority')

        task.category = request.form.get('category')

        db.session.commit()

        app.logger.info(
            f"Task updated: {task.content}"
       )

        return redirect('/')

    return render_template(
        'edit.html',
        task=task
    )
# Run App
if __name__ == '__main__':
    app.run(debug=True)