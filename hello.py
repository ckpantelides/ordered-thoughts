import sqlite3

from flask import Flask, redirect, render_template, request, url_for, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["DEBUG"] = True

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            print("must provide username")
            return render_template("login.html")

        # Ensure password was submitted
        if not request.form.get("password"):
            print("must provide password")
            return render_template("login.html")

        # Selects username from login form
        username=request.form.get("username")

        # Selects database and cursor object
        db = sqlite3.connect("test.db")
        cursor = db.cursor()

        # Query database for username
        cursor.execute('SELECT * FROM users WHERE Username=?', (username,))

        row = cursor.fetchone()

        # Ensure username exists
        if username != row[1]:
          print("invalid username")
          return render_template('login.html')

        # Ensure password is correct
        if not check_password_hash(row[2], request.form.get("password")):
          print("invalid password")
          return render_template('login.html')

        # Remember which user has logged in
        session["user_id"] = row[0]
        print(session["user_id"])
        db.close()

        # Redirect user to newthought page
        return redirect("/newthought")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
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
        print("must provide username")
        return render_template("register.html")

      # Ensure password was submitted
      if not request.form.get("password"):
        print("must provide password")
        return render_template("register.html")

      # Ensure password confirmation was submitted
      if not request.form.get("confirmation"):
        print("must confirm password")
        return render_template("register.html")

      # Checks password and password confirmation match
      if request.form.get("password") != request.form.get("confirmation"):
        print("password and confirmation don't match")
        return render_template("register.html")

      # selects database and cursor object
      db = sqlite3.connect("test.db")
      cursor = db.cursor()

      # get username and password from register form, hash password with werkzeug
      username = request.form.get("username")
      hash = generate_password_hash(request.form.get("password"))

      # check through all usernames
      cursor.execute('SELECT * FROM users WHERE Username=?', (username,))

      # end registration if username exists
      if cursor.fetchone() is not None:
        print("That username is already taken")
        return render_template('register.html')

      # commit new user to database if username unique
      else:
        cursor.execute('''INSERT INTO users(username, hash)
                  VALUES(?,?)''', (username, hash))
        db.commit()

      print('New user registered')

      # select users data
      cursor.execute('SELECT * FROM users WHERE Username=?', (username,))
      row = cursor.fetchone()

      # save user_id to session, so it can be used as foreign key for new thoughts
      session["user_id"] = row[0]
      print(session["user_id"])

      return render_template("newthought.html")

    else:
      return render_template("register.html")

@app.route('/newthought', methods=["GET", "POST"])
def fileThought():
  """File new thought"""

  if request.method =="POST":

    # Connect to database
    db = sqlite3.connect("test.db")

    # Retrieve category and thought from html
    category = request.form.get("category")
    thought = request.form.get("thought")

    # Insert new thought with session_id into database
    db.execute('''INSERT INTO thoughts(category, thought, user_id)
                  VALUES(?,?,?)''', (category, thought, session["user_id"],))

    print('Successly filed!')

    # Save changes to database and close
    db.commit()
    db.close()
    return render_template("newthought.html")

  else:
    return render_template("newthought.html")

@app.route('/history', methods=["GET", "POST"])
def history():
  """See history of thoughts"""

  # Get history of user's thoughts, group together by category
  db = sqlite3.connect("test.db")
  cursor = db.cursor()

  thoughts = cursor.execute('SELECT * FROM thoughts WHERE user_id=? ORDER BY CATEGORY ASC', (session["user_id"],))

  def nest(thoughts):
    root = {}
    for thought in thoughts:
        d = root
        for item in thought[:-2]:
            d = d.setdefault(item, {})
        d[thought[-2]] = thought[-1]
    return root

  # loop through each thought
#  for thought in thoughts:
#    category = thought[0]
#    thought = thought[1]

  return render_template("history.html", thoughts=thoughts)

#  if request.method =="POST":
#    return render_template("history.html")

#  else:
#    return render_template("history.html")

if __name__ == '__main__':
    app.run()
