from datetime import datetime, timedelta
import pytz
from flask import redirect, session, render_template, flash
from functools import wraps
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

def login_required(f):
    """
    Decorate routes to require login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def verify_login(username, password):
    """Check if username and password are correct"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select id, password from users where username = ?", (username.lower(),)).fetchone()
        if res is not None and check_password_hash(res[1], password):
            return res[0]
        else:
            return None

def register_user(email, username, password):
    """Register user in the app"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        cur.execute("select count(*) as cnt from users where email = ? or username = ?", (email.lower(),username.lower()))
        if cur.fetchone()[0] > 0:
            flash("Email or username already exists")
            return render_template("register.html")
        if not email.count("@") == 1 or not email.count(".") == 1:
            flash("Invalid email address")
            return render_template("register.html")
        cur.execute("insert into users (email, username, password) values (?, ?, ?)", (email.lower(), username, generate_password_hash(password)))
        conn.commit()
        cur.execute("select last_insert_rowid()")
        return cur.fetchone()[0]
    
def change_user_password(user_id, old_password, new_password):
    """Change user's password"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        cur.execute("select password from users where id = ?", (user_id,))
        if not check_password_hash(cur.fetchone()[0], old_password):
            flash("Provided password is incorrect")
            return render_template("change_password.html")
        cur.execute("update users set password = ? where id = ?", (generate_password_hash(new_password), user_id))
        conn.commit()
    return True

def calculate_streaks(entries):
    # Convert strings to datetime objects and sort them
    dates = sorted(set(datetime.strptime(date, '%Y-%m-%d').date() for date in entries))

    # Calculate the current streak
    today = datetime.now().date()
    current_streak = 0

    while today in dates:
        current_streak += 1
        today -= timedelta(days=1)

    # Calculate the maximum streak
    max_streak = 0
    streak = 0
    last_date = None

    for date in dates:
        if last_date is None or (date - last_date).days == 1:
            streak += 1
        else:
            max_streak = max(max_streak, streak)
            streak = 1  # Reset streak for the new sequence
        last_date = date

    max_streak = max(max_streak, streak)  # Final check for the last streak

    return current_streak, max_streak

def get_entry_from_id(entry_id):
    """Get entry from database based on id"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select entry, created_at from journal where id = ?", (entry_id,))
        entry = res.fetchone()
        if entry is None:
            return None, datetime.fromisoformat(datetime.now(pytz.timezone('Europe/Warsaw')).strftime('%Y-%m-%d')).strftime("%d %B %Y")
        else:
            return entry[0], datetime.fromisoformat(entry[1]).strftime("%d %B %Y")
    
def get_today_entry_id(user_id):
    """Get today entry id from database"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select id from journal where created_at = ? and user_id = ?", (datetime.now(pytz.timezone('Europe/Warsaw')).strftime('%Y-%m-%d'), user_id))
        try:
            return res.fetchone()[0]
        except:
            return None

def get_user_config(user_id):
    """Get user configuration"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select weekly_goal from users where id = ?", (user_id,))
        return res.fetchone()[0]

def update_user_config(user_id, weekly_goal):
    """Update user configuration"""
    try:
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute("update users set weekly_goal = ? where id = ?", (weekly_goal, user_id))
            conn.commit()
        session["weekly_goal"] = int(weekly_goal)
        return True
    except Exception:
        return False

def get_entries_stats(user_id):
    """Get entries stats for given user id, used on Home Dashboard"""
    with sqlite3.connect("myJournal.db") as conn:
        cur = conn.cursor()
        res = cur.execute("select created_at, word_count from journal where user_id = ? order by id desc", (user_id,))
        journal_entries = res.fetchall()
    if journal_entries is None or len(journal_entries) == 0:
        return 0, 0, 0, 0, 0, 0
    journal_dates = [entry[0] for entry in journal_entries]
    total_entries = len(journal_dates)
    word_count = sum(entry[1] for entry in journal_entries)
    avg_count = int(word_count / total_entries)
    current_streak, max_streak = calculate_streaks(journal_dates)
    entries_this_week = len([entry for entry in journal_dates if datetime.strptime(entry, '%Y-%m-%d').date() >= datetime.now(pytz.timezone('Europe/Warsaw')).date() - timedelta(days=7)])
    return total_entries, word_count, avg_count, current_streak, max_streak, entries_this_week

def update_today_entry(user_id, entry_id, entry, word_count):
    """Update today entry in database"""
    try:
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            today_entry_cnt = cur.execute("select word_count from journal where id = ?", (entry_id,)).fetchone()[0]
            cur.execute("update journal set entry = ?, word_count = ? where id = ?", (entry, word_count, entry_id))
            conn.commit()
        session["word_count"] += word_count - today_entry_cnt
        session["avg_count"] = int(session["word_count"] / session["total_entries"])
        return True
    except Exception:
        return False

def add_today_entry(user_id, entry, word_count):
    """Add today entry to database"""
    try:
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            cur.execute(
                "insert into journal (entry, created_at, user_id, word_count) values (?, ?, ?, ?)",
                (entry, datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"), session["user_id"], word_count),
                )
            cur.execute("select last_insert_rowid()")
            session["entry_id"] = cur.fetchone()[0]
            conn.commit()
        session["word_count"] += word_count
        session["total_entries"] += 1
        session["avg_count"] = int(session["word_count"] / session["total_entries"])
        session["entries_this_week"] += 1
        session["current_streak"] += 1
        session["max_streak"] = max(session["max_streak"], session["current_streak"])
        return True
    except Exception:
        return False

def get_journal_calendar(user_id):
    """Get dict of user's journal entries"""
    try:
        with sqlite3.connect("myJournal.db") as conn:
            cur = conn.cursor()
            res = cur.execute(
                "select id, created_at from journal where user_id = ?",
                (user_id,),
            )
            journal_entries = res.fetchall()
        # Get dict of entries {date:id}
        journal_entries = {date: entry_id for entry_id, date in journal_entries}
        return journal_entries
    except Exception:
        return None
class User:
    """
    User class that caches user information in session.
    It stores all user info used in application.
    """
    def __init__(self, user_id, new_user=False):
        self.user_id = user_id
        if new_user:
            self.weekly_goal = 0
            self.entry_id = None
            self.total_entries = 0
            self.word_count = 0
            self.avg_count = 0
            self.current_streak = 0
            self.max_streak = 0
            self.entries_this_week = 0
        else:
            self.weekly_goal = get_user_config(self.user_id)
            self.entry_id = get_today_entry_id(self.user_id)
            self.total_entries, self.word_count, self.avg_count, self.current_streak, self.max_streak, self.entries_this_week = get_entries_stats(self.user_id)
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'weekly_goal': self.weekly_goal,
            'entry_id': self.entry_id,
            'total_entries': self.total_entries,
            'word_count': self.word_count,
            'avg_count': self.avg_count,
            'current_streak': self.current_streak,
            'max_streak': self.max_streak,
            'entries_this_week': self.entries_this_week
        }
    
    

    
    