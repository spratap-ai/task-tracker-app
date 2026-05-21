from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Task Tracker App</h1>
    <p>My first cloud deployment project 🚀</p>
    """

@app.route('/about')
def about():
    return "<h2>This app is running using Flask!</h2>"

if __name__ == '__main__':
    app.run(debug=True)