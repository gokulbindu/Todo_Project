from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    due_datetime = db.Column(db.DateTime)

    def __init__(self, title, complete, due_datetime):
        self.title = title
        self.complete = complete
        self.due_datetime = due_datetime

@app.route("/")
def home():
    try:
        todo_list = Todo.query.all()
        return render_template("base.html", todo_list=todo_list)
    except Exception as e:
        print("An error occurred in home Function:", e)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    due_datetime_str = request.form.get("due_datetime")

    if not title:
        flash("Error: No title is added", "error")
        return redirect(url_for("home"))

    if not due_datetime_str:
        flash("Error: No Time is added", "error")
        return redirect(url_for("home"))

    due_datetime = datetime.fromisoformat(due_datetime_str)

    if due_datetime < datetime.now():
        flash("Error: Selected time is not valid. Please select a future time.", "error")
        return redirect(url_for("home"))

    new_todo = Todo(title=title, complete=False, due_datetime=due_datetime)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<int:todo_id>", methods=["POST"])
def edit(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_title = request.form.get("new_title")
    new_due_datetime_str = request.form.get("new_due_datetime")
    new_due_datetime = datetime.fromisoformat(new_due_datetime_str)
    todo.title = new_title
    todo.due_datetime = new_due_datetime
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

def auto_mark_complete():
    while True:
        try:
            with app.app_context():
                todos = Todo.query.filter_by(complete=False).all()
                for todo in todos:
                    if todo.due_datetime <= datetime.now():
                        todo.complete = True
                db.session.commit()
            time.sleep(60)
        except Exception as e:
            print("An error occurred in auto_mark_complete:", e)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    auto_mark_thread = threading.Thread(target=auto_mark_complete)
    auto_mark_thread.start()

    app.run(debug=True)
