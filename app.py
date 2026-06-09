from flask import Flask, request, redirect, render_template
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
import os
import logging

load_dotenv()

app = Flask(__name__)
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


# Database Table
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Pending")
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default="Medium")
    category = db.Column(db.String(50), default="Work")



# Home Page
@app.route('/')
def home():

    search = request.args.get('search')
    priority_filter = request.args.get('priority_filter')
    status_filter = request.args.get('status_filter')
    category_filter = request.args.get('category_filter')

    query = Task.query

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

    today = date.today()

    return render_template(
        "index.html",
        tasks=tasks,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        today=today
    )
# Add Task
@app.route('/add', methods=['POST'])
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
    category=category
    ) 
        db.session.add(new_task)
        db.session.commit()
        app.logger.info(
            f"Task created: {task_content}"
   )

    return redirect('/')

@app.route('/complete/<int:id>')
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