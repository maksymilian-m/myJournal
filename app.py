from datetime import datetime, timedelta
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

# App
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def calculate_streaks(entries):
    sorted_entries = sorted(entries, key=lambda x: x['date'], reverse=True)
    current_streak = 0
    max_streak = 0
    streak_active = True
    
    for i in range(len(sorted_entries) - 1):
        current_date = datetime.strptime(sorted_entries[i]['date'], '%Y-%m-%d')
        next_date = datetime.strptime(sorted_entries[i+1]['date'], '%Y-%m-%d')
        if (current_date - next_date).days == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            streak_active = False
            current_streak = 0

    if streak_active:
        current_streak += 1
        max_streak = max(max_streak, current_streak)

    if not(sorted_entries[-1]['date'] == datetime.now(pytz.timezone('Europe/Warsaw')).strftime('%Y-%m-%d')):
        current_streak = 0
    return current_streak, max_streak
@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("home"))
    else:
        return render_template("landing.html")

@app.route("/home")
@login_required
def home():
    """Home Page presenting user dashboard"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select id, entry, created_at, word_count from journal where user_id = ? order by id", (session["user_id"],))
        journal_entries = res.fetchall()
    if journal_entries is None:
        return render_template("home.html", total_entries=0, word_count=0, avg_count=0, weekly_goal=0, goal_achieved=False, current_streak=0, max_streak=0)
    journal_entries = [{'id': entry[0], 'entry': entry[1], 'date': entry[2], 'word_count': entry[3]} for entry in journal_entries]
    total_entries = len(journal_entries)
    word_count = sum(entry['word_count'] for entry in journal_entries)
    avg_count = int(word_count / total_entries)

    # Goals
    weekly_goal = 5  # example weekly goal, to be configured
    # get entries from this week starting from Monday
    start_date = datetime.now(pytz.timezone('Europe/Warsaw')).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=7)

    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select count(*) from journal where user_id = ? and created_at >= ? and created_at < ?", (session["user_id"], start_date, end_date))
        entries_this_week = res.fetchone()[0]
    goal_achieved = entries_this_week >= weekly_goal

    # Streaks
    current_streak, max_streak = calculate_streaks(journal_entries)

    return render_template("home.html", total_entries=total_entries,
                           word_count=word_count, avg_count=avg_count,
                           weekly_goal=weekly_goal, goal_achieved=goal_achieved,
                           current_streak=current_streak, max_streak=max_streak)

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
        session["user_id"] = res[0]
        
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
        res = cur.execute("select entry, created_at from journal where id = ?", (entry_id,))
        return res.fetchone()

def get_today_user_entry(user_id, date):
    """Get entry from database based on user id and date"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select entry, created_at from journal where user_id = ? and created_at = ?", (user_id, date))
        result = res.fetchone()
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
        # count words in entry
        word_count = len(entry.split())
        # Add entry to database
        if session.get("entry_id"):
            with sqlite3.connect("myJournal.db") as conn:
                cur = conn.cursor()
                cur.execute(
                    "update journal set entry = ?, word_count = ? where id = ?",
                    (entry, session["entry_id"], word_count),
                )
                conn.commit()
        else:
            with sqlite3.connect("myJournal.db") as conn:
                cur = conn.cursor()
                cur.execute(
                    "insert into journal (entry, created_at, user_id, word_count) values (?, ?, ?, ?)",
                    (entry, datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"), session["user_id"], word_count),
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
        res = cur.execute(
            "select id, created_at from journal where user_id = ?",
            (session["user_id"],),
        )
        journal_entries = res.fetchall()
        # Get dict of entries {date:id}
        journal_entries = {date: entry_id for entry_id, date in journal_entries}
        current_date = datetime.now()
    return render_template("calendar.html", current_date=current_date, journal_entries=journal_entries)


@app.route("/config", methods=["GET", "POST"])
@login_required
def config():
    """Displaying journal configuration"""
    if request.method == "POST":
        weekly_goal =request.form.get("weekly-goal-slider")
        if not weekly_goal or int(weekly_goal) < 1 or int(weekly_goal) > 7:
            flash("Weekly goal should be between 1 and 7")
            return redirect("/config")
        
        prompts_enabled = request.form.get("toggle-prompts")
        if not prompts_enabled or prompts_enabled != "true":
            prompts_enabled = 0
        
        prompts = request.form.getlist("prompts")
        
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "update users set weekly_goal = ?, prompts_enabled = ? where id = ?",
                (weekly_goal, prompts_enabled, session["user_id"]),
            )
            if prompts:
                # createa list of tuples with user id and prompt
                prompts = [(session["user_id"], prompt) for prompt in prompts]
                cur.execute(
                    "delete from prompts where user_id = ?",
                    (session["user_id"],),
                )
                cur.executemany("insert into prompts (user_id, prompt) values (?, ?)", prompts)
            conn.commit()
        flash("Configuration of journal updated!")
        return redirect("/")
    else:
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            res = cur.execute(
                "select weekly_goal, prompts_enabled from users where id = ?",
                (session["user_id"],),
            )
            result = res.fetchone()
            weekly_goal, prompts_enabled = result
            prompts = cur.execute("select prompt from prompts where user_id = ?", (session["user_id"],)).fetchall()
            if not prompts:
                prompts = ["What are you grateful for today?",
                           "What was the highlight of your day?",
                           "What did you learn today?",
                           "Describe a challenge you faced and how you overcame it.",
                           "What made you smile today?"]
        return render_template("config.html", weekly_goal=weekly_goal, prompts_enabled=prompts_enabled, prompts=prompts)

if __name__ == '__main__':
    app.run(debug=True)