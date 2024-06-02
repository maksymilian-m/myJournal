from datetime import datetime
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
import pytz
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create connection and cursor at application level
#with app.app_context():
#    db = sqlite3.connect("myJournal.db")
#    cur = db.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Home Page presenting some dashboard with user stats"""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            flash("Please provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not password:
            flash("Please provide password")
            return render_template("login.html")

        # Query database for user
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute(
            "SELECT id, password FROM users WHERE username = ?",
            (username.lower(),)
            )
            res = cur.fetchone()

        # Ensure username exists and password is correct
        if res is None or not check_password_hash(res[1], password):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = res[1]
        
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user in the app"""
    if request.method == "POST":
        # Get email
        email = request.form.get("email")
        # Validate email
        if not email:
            flash("Please provide your email!")
            return render_template("register.html")
        else:
            # Check if email is already taken
            with sqlite3.connect("myJournal.db") as conn:
                cur = conn.cursor()
                cur.execute(
                    "select count(*) as cnt from users where email = ?", (email.lower(),)
                    )
                email_exists = cur.fetchone()[0]
            if email_exists > 0:
                flash("This email is already registered, please use different one!")
                return render_template("register.html")
            # Check if email is valid
            if not email.count("@") == 1 or not email.count(".") == 1:
                flash("Please provide a valid email address!")
                return render_template("register.html")
        # Get username
        username = request.form.get("username")
        # Validate username
        if not username:
            flash("Please provide your username!") #TODO: error message
            return render_template("register.html")
        else:
            # Check if username is already taken
            with sqlite3.connect("myJournal.db") as conn:
                cur = conn.cursor()
                cur.execute(
                "select count(*) as cnt from users where username = ?", (username.lower(),)
                )
                user_exists = cur.fetchone()[0]
            if user_exists > 0:
                flash("This username is taken, please choose different one!")
                return render_template("register.html")
        password = request.form.get("password")
        if not password:
            flash("Please provide your password!")
            return render_template("register.html")
        confirmation = request.form.get("confirmation")
        if not confirmation:
            flash("Please confirm your password!")
            return render_template("register.html")
        if password != confirmation:
            flash("Passwords do not match!")
            return render_template("register.html")
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "insert into users(username, password, email) values(?, ?, ?)",
                (username.lower(),
                generate_password_hash(password),
                email.lower()
                ))
            conn.commit()
        flash("You were successfully registered!")
        return redirect("/")
    return render_template("register.html")
    


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Changes user's password"""
    if request.method == "POST":
        old_password = request.form.get("old_password")
        if not old_password:
            flash("Please provide an existing password")
            return render_template("change_password.html")
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute("select password from users where id = ?", (session["user_id"],))
            existing_password = cur.fetchone()[0]
        if not check_password_hash(existing_password, old_password):
            flash("Provided password is incorrect")
            return render_template("change_password.html")
        new_password = request.form.get("new_password")
        if not new_password or new_password == old_password:
            flash("Please provide a new password")
            return render_template("change_password.html")
        confirmation = request.form.get("confirmation")
        if not confirmation or confirmation != new_password:
            flash("Please confirm a new password")
            return render_template("change_password.html")
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "update users set password = ? where id = ?",
                (generate_password_hash(new_password), session["user_id"]),
            )
            conn.commit()
        flash("Password successfully changed!")
        return redirect("/")
    else:
        return render_template("change_password.html")

def get_entry_from_id(entry_id):
    """Get entry from database based on id"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        cur.execute("select entry, created_at from journal where id = ?", (entry_id,))
        return cur.fetchone()

def get_today_user_entry(user_id, date):
    """Get entry from database based on user id and date"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        cur.execute("select entry, created_at from journal where user_id = ? and created_at = ?", (user_id, date))
        result = cur.fetchone()
        return result if result else (None, None)

@app.route("/entry", methods=["GET", "POST"])
@login_required
def entry():
    """Creates new entry"""
    if request.method == "POST":
        entry = request.form.get("content")
        if not entry:
            flash("Please provide an entry")
            return render_template("entry.html")
        # Trim leading and trailing whitespaces from entry
        entry = entry.strip()
        # Add entry to database
        if session.get("entry_id"):
            with sqlite3.connect("myJournal.db") as conn:
                cur = conn.cursor()
                cur.execute(
                    "update journal set entry = ? where id = ?",
                    (entry, session["entry_id"]),
                )
                conn.commit()
        else:
            with sqlite3.connect("myJournal.db") as conn:
                cur = conn.cursor()
                cur.execute(
                    "insert into journal (entry, created_at, user_id) values (?, ?, ?)",
                    (entry, datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"), session["user_id"]),
                )
                conn.commit()
        flash("Your Journal has been successfully updated!")
        return redirect("/")
    else:
        entry, date = get_today_user_entry(session["user_id"], datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"))
        if entry is None:
            entry = ""
            date = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%d %B %Y")
        else:
            date = datetime.fromisoformat(date).strftime("%d %B %Y")
            session["entry_id"] = entry
        return render_template("entry.html", date=date, entry=entry)

@app.route('/entry/<int:entry_id>', methods=['GET'])
def show_entry(entry_id):
    # Retrieve the journal entry from the database using entry_id
    entry, date = get_entry_from_id(entry_id)
    date = datetime.fromisoformat(date).strftime("%d %B %Y")
    return render_template('entry.html', entry=entry, date=date)

@app.route("/calendar")
@login_required
def calendar():
    """Displays a calendar with history of entries"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "select id, created_at from journal where user_id = ?",
            (session["user_id"],),
        )
        journal_entries = cur.fetchall()
        # Get dict of entries {date:id}
        journal_entries = {date: entry_id for entry_id, date in journal_entries}
        current_date = datetime.now()
    return render_template("calendar.html", current_date=current_date, journal_entries=journal_entries)


@app.route("/config", methods=["GET", "POST"])
@login_required
def config():
    """Displaying journal configuration"""
    if request.method == "POST":
        flash("Configuration of journal updated!")
        return redirect("/")
    else:
        return render_template("config.html")
