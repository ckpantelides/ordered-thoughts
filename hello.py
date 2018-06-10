import sqlite3, html
import os
import psycopg2

from flask import Flask, redirect, render_template, request, url_for, session, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from collections import defaultdict
from functools import wraps

app = Flask(__name__)
app.config["DEBUG"] = True

app.secret_key = SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# unwanted html characters with safe replacements
html_escape_table = {
  "&": "&amp;",
  '"': "&quot;",
  "'": "&apos;",
  ">": "&gt;",
  "<": "&lt;",
  }

# function to replace unwanted html characters (from users' html forms)
def html_escape(text):
  """Produce entities within text."""
  return "".join(html_escape_table.get(c,c) for c in text)

# function to require login using flask decorator
def login_required(f):
    """Decorate routes to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # keeps user logged in when browser closed
    session.permanent = True

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("must provide password")
            return render_template("login.html")

        # Selects username from login form, escapes harmful characters
        # forces lowercase
        username= html_escape(request.form.get("username"))
        username= username.lower()

        # Opens cursor to perform db operation
        cur = conn.cursor()

        # Query database for username
        cur.execute('SELECT * FROM users WHERE Username=(%s)', (username,))

        row = cur.fetchone()

        # Ensure username exists
        if row == None:
          flash("invalid username")
          return render_template('login.html')

        # Turns password lowercase
        password = (request.form.get("password")).lower()

        # Ensure password is correct
        if not check_password_hash(row[2], password):
          flash("invalid password")
          return render_template('login.html')

        # Remember which user has logged in
        session["user_id"] = row[0]

        conn.close()

        # Redirect user to newthought page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

      # Ensure username was submitted
      if not request.form.get("username"):
        flash("must provide username")
        return render_template("register.html")

      # Ensure password was submitted
      if not request.form.get("password"):
        flash("must provide password")
        return render_template("register.html")

      # Ensure password confirmation was submitted
      if not request.form.get("confirmation"):
        flash("must confirm password")
        return render_template("register.html")

      # Checks password and password confirmation match
      if request.form.get("password") != request.form.get("confirmation"):
        flash("password and confirmation don't match")
        return render_template("register.html")

      # opens cursor object for db operations
      cur = conn.cursor()

      # get username and password from register form,
      # hash password with werkzeug, force lowercase
      username = (html_escape(request.form.get("username"))).lower()
      password = (html_escape(request.form.get("password"))).lower()
      hash = generate_password_hash(password)

      # check through all usernames
      cur.execute('SELECT * FROM users WHERE Username=(%s)', (username,))

      # end registration if username exists
      if cur.fetchone() is not None:
        flash("That username is already taken")
        return render_template('register.html')

      # commit new user to database if username unique
      else:
        cur.execute('''INSERT INTO users(username, hash)
                  VALUES(%s,%s)''', (username, hash))
        conn.commit()

      flash('New user registered')

      # select users data
      cur.execute('SELECT * FROM users WHERE Username=(%s)', (username,))
      row = cur.fetchone()

      # save user_id to session, so it can be used as foreign key for new thoughts
      session["user_id"] = row[0]

      return render_template("newthought.html")

    else:
      return render_template("register.html")

@app.route('/', methods=["GET", "POST"])
@login_required
def fileThought():
  """File new thought"""

  if request.method =="POST":

    # Retrieve category and thought from html
    # Ensure category is lowercase
    category = request.form.get("category").lower()
    thought = request.form.get("thought")

    # Ensure new tought was submitted
    if not request.form.get("thought"):
      flash("what are you thinking?")
      return render_template("newthought.html")

    # Ensure category was submitted
    if not request.form.get("category"):
      flash("category please")
      return render_template("newthought.html")

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Insert new thought with session_id into database
    cur.execute('''INSERT INTO thoughts(category, thought, user_id)
                  VALUES(%s,%s,%s)''', (category, thought, session["user_id"],))

    flash('Successly filed!')

    # Save changes to database and close
    conn.commit()
    conn.close()

    return render_template("newthought.html")

  else:
    return render_template("newthought.html")

@app.route('/history', methods=["GET", "POST"])
@login_required
def history():
  """See history of thoughts"""

  # Get history of user's thoughts, group together by category
  cur = conn.cursor()
  cur.execute('SELECT category, thought FROM thoughts WHERE user_id=(%s) ORDER BY CATEGORY ASC', (session["user_id"],))
  collected_thoughts = cur.fetchall()

  # use default dict to reorganise users thoughts by its category key value
  thoughts_by_category = defaultdict(list)
  for category, thought in collected_thoughts:
    thoughts_by_category[category].append(thought)

  # pass thoughts_by_category dict into history.html, organise dict using .items() method
  return render_template("history.html", thoughts_by_category=thoughts_by_category.items())

@app.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
  """Edit thoughts"""

  if request.method =="GET":

      # Get history of user's thoughts, group together by category
      cur = conn.cursor()

      cur.execute('SELECT category, thought FROM thoughts WHERE user_id=(%s) ORDER BY CATEGORY ASC', (session["user_id"],))
      collected_thoughts = cur.fetchall()

      # use default dict to reorganise users thoughts by its category key value
      thoughts_by_category = defaultdict(list)
      for category, thought in collected_thoughts:
          thoughts_by_category[category].append(thought)

      # pass thoughts_by_category dict into edit.html, organise dict using .items() method
      return render_template("edit.html", thoughts_by_category=thoughts_by_category.items())

  if request.method =="POST":

      # get thought to be deleted from html
      elem = request.form.get("editbutton")

      cur = conn.cursor()

      # delete thought where user_id and thought match
      cur.execute('DELETE FROM thoughts WHERE user_id=(%s) AND thought=(%s)', (session["user_id"], elem,))

      # Save changes to database
      conn.commit()

      cur.execute('SELECT category, thought FROM thoughts WHERE user_id=(%s) ORDER BY CATEGORY ASC', (session["user_id"],))
      collected_thoughts = cur.fetchall()

      # use default dict to reorganise users thoughts by its category key value
      thoughts_by_category = defaultdict(list)
      for category, thought in collected_thoughts:
          thoughts_by_category[category].append(thought)

      # pass thoughts_by_category dict into edit.html, organise dict using .items() method
      return render_template("edit.html", thoughts_by_category=thoughts_by_category.items())

if __name__ == '__main__':
    app.run()
