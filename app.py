from flask import Flask, request, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres123@localhost/tasktrackerdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Table
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

# HTML
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Tracker</title>
</head>
<body>

<h1>Task Tracker App 🚀</h1>

<form method="POST" action="/add">
    <input type="text" name="task" placeholder="Enter task" required>
    <button type="submit">Add Task</button>
</form>

<h2>Tasks:</h2>

<ul>
{% for task in tasks %}
    <li>
        {{ task.content }}
        <a href="/delete/{{ task.id }}">Delete</a>
    </li>
{% endfor %}
</ul>

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
    with app.app_context():
        db.create_all()

    app.run(debug=True)