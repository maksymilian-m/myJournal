from datetime import datetime, timedelta

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
import pytz
from helpers import login_required, User, verify_login, add_today_entry, update_today_entry, get_entry_from_id, get_journal_calendar, update_user_config, register_user, change_user_password

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# App
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("home"))
    else:
        return render_template("landing.html")

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

        # Ensure username and password are correct
        user_id = verify_login(username, password)

        if user_id is None:
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Cache user data
        session.update(User(user_id).to_dict())

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

    # Redirect user to landing page
    return redirect("/")


@app.route("/home")
@login_required
def home():
    """Home Page presenting user dashboard"""
    # Goals
    print(f"entries_this_week: {session['entries_this_week']}, weekly_goal: {session['weekly_goal']}")
    goal_achieved = session["entries_this_week"] >= session["weekly_goal"]

    return render_template("home.html", total_entries=session["total_entries"],
                           word_count=session["word_count"], avg_count=session["avg_count"],
                           weekly_goal=session["weekly_goal"], goal_achieved=goal_achieved,
                           current_streak=session["current_streak"], max_streak=session["max_streak"])



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
        # Get username
        username = request.form.get("username")
        if not username:
            flash("Please provide your username!")
            return render_template("register.html")
        password = request.form.get("password")
        if not password:
            flash("Please provide your password!")
            return render_template("register.html")
        confirmation = request.form.get("confirmation")
        if not confirmation or confirmation != password:
            flash("Please confirm your password!")
            return render_template("register.html")
        user_id = register_user(email, username, password)

        # Cache user
        session.update(User(user_id, new_user=True).to_dict())

        # Redirect user to home page
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
        new_password = request.form.get("new_password")
        if not new_password or new_password == old_password:
            flash("Please provide a new password")
            return render_template("change_password.html")
        confirmation = request.form.get("confirmation")
        if not confirmation or confirmation != new_password:
            flash("Please confirm a new password")
            return render_template("change_password.html")
        if not change_user_password(session["user_id"], old_password, new_password):
            flash("Something went wrong, please try again!")
            return render_template("change_password.html")
        flash("Password successfully changed!")
        return redirect("/")
    else:
        return render_template("change_password.html")

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
        # count words in entry
        word_count = len(entry.split())
        # Add entry to database
        if session.get("entry_id"):
            if not(update_today_entry(session["user_id"], session["entry_id"], entry, word_count)):
                flash("Something went wrong, please try again!")
                return render_template("entry.html")
        else:
            if not(add_today_entry(session["user_id"], entry, word_count)):
                flash("Something went wrong, please try again!")
                return render_template("entry.html")
        flash("Your Journal has been successfully updated!")
        return redirect("/")
    else:
        if session.get("entry_id"):
            entry, date = get_entry_from_id(session["entry_id"])
        else:
            entry = None
            date = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%d %B %Y")
        return render_template("entry.html", date=date, entry=entry, prompts_enabled = session["prompts_enabled"], readonly=False)

@app.route('/entry/<int:entry_id>', methods=['GET'])
def show_entry(entry_id):
    # Retrieve the journal entry from the database using entry_id
    entry, date = get_entry_from_id(entry_id)
    date = datetime.fromisoformat(date).strftime("%d %B %Y")
    return render_template('entry.html', entry=entry, date=date, prompts_enabled=False, readonly=True)

@app.route("/calendar")
@login_required
def calendar():
    """Displays a calendar with history of entries"""
    journal_entries = get_journal_calendar(session["user_id"])
    current_date = datetime.now()
    return render_template("calendar.html", current_date=current_date, journal_entries=journal_entries)


@app.route("/config", methods=["GET", "POST"])
@login_required
def config():
    """Displaying journal configuration"""
    if request.method == "POST":
        weekly_goal = request.form.get("weekly-goal")
        if not weekly_goal or int(weekly_goal) < 0 or int(weekly_goal) > 7:
            flash("Weekly goal should be between 0 and 7")
            return redirect("/config")
        
        prompts_enabled = request.form.get("toggle-prompts")
        if not prompts_enabled or prompts_enabled != "true":
            prompts_enabled = 0
        else:
            prompts_enabled = 1
        
        if not update_user_config(session["user_id"], weekly_goal, prompts_enabled):
            flash("Something went wrong, please try again!")
            return redirect("/config")

        # Redirect to home page
        flash("Configuration of journal updated!")
        return redirect("/")
    else:
        return render_template("config.html", weekly_goal=session["weekly_goal"], prompts_enabled=session["prompts_enabled"])
