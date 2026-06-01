from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)

# Read database connection string from environment variable
database_url = os.environ.get("DATABASE_URL")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Table
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

# Create Tables Automatically
with app.app_context():
    db.create_all()

# HTML Page
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Tracker</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body class="bg-light">

<nav class="navbar navbar-dark bg-dark">
    <div class="container-fluid">
        <span class="navbar-brand mb-0 h1">
            🚀 Task Tracker App
        </span>
    </div>
</nav>

<div class="container mt-5">

    <div class="card shadow">

        <div class="card-header text-center">
            <h2>🚀 Task Tracker</h2>
        </div>

        <div class="card-body">

            <form method="POST" action="/add">

                <div class="input-group mb-4">

                    <input
                        type="text"
                        name="task"
                        class="form-control"
                        placeholder="Enter a task..."
                        required>

                    <button
                        class="btn btn-primary"
                        type="submit">
                        Add Task
                    </button>

                </div>

            </form>

<h4>Your Tasks</h4>

{% if tasks %}

{% for task in tasks %}

<div class="card mb-2">

    <div class="card-body d-flex justify-content-between">

        <div>
    <strong>{{ task.content }}</strong>
</div>

        <a
            href="/delete/{{ task.id }}"
            class="btn btn-danger btn-sm">
            Delete
        </a>

    </div>

</div>

{% endfor %}

{% else %}

<div class="alert alert-info">
    No tasks added yet.
</div>

{% endif %}

        </div>

    </div>

</div>

</body>
</html>
"""

# Home Page
@app.route('/')
def home():
    tasks = Task.query.all()
    return render_template_string(HTML_PAGE, tasks=tasks)

# Add Task
@app.route('/add', methods=['POST'])
def add_task():
    task_content = request.form.get('task')

    if task_content:
        new_task = Task(content=task_content)
        db.session.add(new_task)
        db.session.commit()

    return redirect('/')

# Delete Task
@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()

    return redirect('/')

# Run App
if __name__ == '__main__':
    app.run(debug=True)