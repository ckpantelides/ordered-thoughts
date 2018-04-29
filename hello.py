import sqlite3

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])

def fileThought():

  if request.method =="POST":

    db = sqlite3.connect("test.db")
    cursor = db.cursor()

    category = request.form.get("category")
    thought = request.form.get("thought")

    cursor.execute('''INSERT INTO thoughts(category, thought)
                  VALUES(?,?)''', (category, thought))

    print('Successly filed!')

    db.commit()

    return render_template("index.html")

  else:
    return render_template("index.html")

if __name__ == '__main__':
    app.run()
