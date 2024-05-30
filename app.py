import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
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
        if not request.form.get("username"):
            flash("Please provide username")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please provide password")
            return redirect("/login")

        # Query database for username
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute(
            "SELECT * FROM users WHERE username = ?",
            request.form.get("username").lower(),
            )
            res = cur.fetchall()

        # Ensure username exists and password is correct
        if len(res) != 1 or not check_password_hash(
            res[0]["hash"], request.form.get("password")
        ):
            flash("Invalid username and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = res[0]["id"]
        
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
            return redirect("/register")
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
                return redirect("/register")
            # Check if email is valid
            if not email.count("@") == 1 or not email.count(".") == 1:
                flash("Please provide a valid email address!")
                return redirect("/register")
        # Get username
        username = request.form.get("username")
        # Validate username
        if not username:
            flash("Please provide your username!") #TODO: error message
            redirect("/register")
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
                return redirect("/register")
        password = request.form.get("password")
        if not password:
            flash("Please provide your password!")
            return redirect("/register")
        confirmation = request.form.get("confirmation")
        if not confirmation:
            flash("Please confirm your password!")
            return redirect("/register")
        if password != confirmation:
            flash("Passwords do not match!")
            return redirect("/register")
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
        """
        old_password = request.form.get("old_password")
        if not old_password:
            return apology("Please provide an existing password")
        existing_password = db.execute(
            "select hash from users where id = ?", session["user_id"]
        )[0]["hash"]
        if not check_password_hash(existing_password, old_password):
            return apology("Existing password incorrect!")
        new_password = request.form.get("new_password")
        if not new_password or new_password == old_password:
            return apology("Please provide a new password")
        confirmation = request.form.get("confirmation")
        if not confirmation or confirmation != new_password:
            return apology("Please confirm a new password")
        db.execute(
            "update users set hash = ? where id = ?",
            generate_password_hash(new_password),
            session["user_id"],
        )
        """
        flash("Password successfully changed!")
        return redirect("/")
    else:
        return render_template("change_password.html")


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Creates new entry"""
    if request.method == "POST":
        flash("New entry added to Your Journal, well done!")
        return redirect("/")
    else:
        return render_template("create.html")


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Displays a history of entries"""
    if request.method == "POST":
        flash("History")
        return redirect("/")
    else:
        return render_template("history.html")


@app.route("/config", methods=["GET", "POST"])
@login_required
def config():
    """Displaying journal configuration"""
    if request.method == "POST":
        flash("Configuration of journal updated!")
        return redirect("/")
    else:
        return render_template("config.html")
