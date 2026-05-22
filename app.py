from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

tasks = []

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Task Tracker</title>
</head>
<body>
    <h1>Shivendra Tracker App 🚀</h1>

    <form method="POST" action="/add">
        <input type="text" name="task" placeholder="Enter task" required>
        <button type="submit">Add Task</button>
    </form>

    <h2>Tasks:</h2>

    <ul>
    {% for task in tasks %}
        <li>
            {{ task }}
            <a href="/delete/{{ loop.index0 }}">Delete</a>
        </li>
    {% endfor %}
    </ul>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE, tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    if task:
        tasks.append(task)
    return redirect('/')

@app.route('/delete/<int:index>')
def delete_task(index):
    if 0 <= index < len(tasks):
        tasks.pop(index)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)