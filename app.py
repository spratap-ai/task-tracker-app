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
from flask import Flask, request, redirect, render_template, flash
from datetime import datetime, date, UTC
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from sqlalchemy import case
from flask_wtf.csrf import CSRFProtect
import os
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get(
    "SECRET_KEY"
)
csrf = CSRFProtect(app)
app.logger.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Read database connection string from environment variable
if os.environ.get("PYTEST_RUNNING"):
    database_url = os.environ.get("TEST_DATABASE_URL")
else:
    database_url = os.environ.get("DATABASE_URL")

if not database_url:
    raise ValueError("Database URL is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = None

# Database Tables

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(200))
@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
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
        if len(password) < 8:

            flash(
                  "Password must be at least 8 characters long",
                  "danger"
            )

            return redirect('/register')

        hashed_password = generate_password_hash(password)
        
        existing_user = User.query.filter(
            (User.email == email) |
            (User.username == username)
        ).first()

        if existing_user:

            flash(
                "Username or email already exists",
                "danger"
            )

            return redirect('/register')

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

        flash("Invalid email or password", "danger")
        return redirect('/login')

    return render_template(
        'login.html'
    )

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/login')

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    if request.method == 'POST':

        current_password = request.form.get(
            'current_password'
        )

        new_password = request.form.get(
            'new_password'
        )

        if len(new_password) < 8:
            flash(
                  "Password must be at least 8 characters long",
                  "danger"
            )
            return redirect('/change-password')

        if not check_password_hash(
            current_user.password_hash,
            current_password
        ):

            return "Current password is incorrect"

        current_user.password_hash = (
            generate_password_hash(
                new_password
            )
        )

        db.session.commit()

        logout_user()

        flash(
            "Password changed successfully. Please log in again.",
            "success"
       )

        return redirect('/login')
    
    return render_template(
        'change_password.html'
    )
@app.route('/profile')
@login_required
def profile():

    tasks = Task.query.filter_by(
        user_id=current_user.id
    ).all()

    total_tasks = len(tasks)

    completed_tasks = len(
        [
            task for task in tasks
            if task.status == "Completed"
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
        "profile.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=completion_rate
    )

# Home Page
@app.route('/')
@login_required
def home():

    search = request.args.get('search')
    priority_filter = request.args.get('priority_filter')
    status_filter = request.args.get('status_filter')
    category_filter = request.args.get('category_filter')
    sort_by = request.args.get('sort_by')
    page = request.args.get(
        'page',
        1,
        type=int
    )

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

    # Sorting
    if sort_by == "due_date":

        query = query.order_by(
            Task.due_date.asc()
        )

    elif sort_by == "priority":

        query = query.order_by(
            case(
                (Task.priority == "High", 1),
                (Task.priority == "Medium", 2),
                (Task.priority == "Low", 3)
            )
       )

    elif sort_by == "newest":

        query = query.order_by(
            Task.created_at.desc()
        )

    elif sort_by == "oldest":

        query = query.order_by(
            Task.created_at.asc()
        )

    else:

        query = query.order_by(
            Task.due_date.asc()
        )

    pagination = query.paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    all_tasks = query.all()

    tasks = pagination.items

    total_tasks = len(all_tasks)

    pending_tasks = len(
    [task for task in all_tasks if task.status == "Pending"]
   )

    completed_tasks = len(
    [task for task in all_tasks if task.status == "Completed"]
    )

    work_tasks = len(
    [task for task in all_tasks if task.category == "Work"]
   )

    personal_tasks = len(
    [task for task in all_tasks if task.category == "Personal"]
   )

    learning_tasks = len(
    [task for task in all_tasks if task.category == "Learning"]
   )

    finance_tasks = len(
    [task for task in all_tasks if task.category == "Finance"]
    )

    today = date.today()

    high_priority_tasks = len(
        [
            task for task in all_tasks
            if task.priority == "High"
            and task.status != "Completed"
        ]
    )

    overdue_tasks = len(
        [
            task for task in all_tasks
            if task.due_date
            and task.due_date < today
            and task.status != "Completed"
        ]
    )

    due_today_tasks = len(
        [
            task for task in all_tasks
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
        pagination=pagination,
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
        flash(
            "Task created successfully!",
            "success"
        )
        app.logger.info(
            f"Task created: {task_content}"
   )

    return redirect('/')

@app.route('/complete/<int:id>')
@login_required
def complete_task(id):

    task = Task.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    task.status = "Completed"

    db.session.commit()
    flash(
        "Task marked as completed!",
        "success"
    )
    app.logger.info(
        f"Task completed: {task.content}"
    )

    return redirect('/')

# Delete Task
@app.route('/delete/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    app.logger.info(
        f"Task deleted: {task.content}"
    )
    db.session.delete(task)
    db.session.commit()

    flash(
    "Task deleted successfully",
    "danger"
    ) 

    return redirect('/')

#Edit Task
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):

    task = Task.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

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
        flash(
           "Task updated successfully",
           "info"
        )

        app.logger.info(
            f"Task updated: {task.content}"
       )

        return redirect('/')

    return render_template(
        'edit.html',
        task=task
    )
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500
# Run App
if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_ENV") == "development"
    )