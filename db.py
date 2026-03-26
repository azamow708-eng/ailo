import sqlite3
from datetime import datetime, timedelta
from config import DATABASE

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Subscriptions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        language TEXT DEFAULT 'en',
        subscription BOOLEAN DEFAULT 0,
        plan_type TEXT,
        expire_date TEXT,
        role TEXT DEFAULT 'user',
        last_payment TEXT
    )
    """)
    # Referrals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        referrer_id INTEGER,
        referee_id INTEGER,
        bonus_days INTEGER,
        used BOOLEAN DEFAULT 0,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subscriptions WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def set_language(user_id, lang):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO subscriptions (user_id, language) VALUES (?, ?)", (user_id, lang))
    cursor.execute("UPDATE subscriptions SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def update_subscription(user_id, plan=None, expire_date=None):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if plan and not expire_date:
        if plan=="1d":
            expire_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        elif plan=="7d":
            expire_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        elif plan=="30d":
            expire_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT OR REPLACE INTO subscriptions (user_id, subscription, plan_type, expire_date, last_payment, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, True, plan, expire_date, now, 'pro'))
    conn.commit()
    conn.close()

def add_referral(referrer_id, referee_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO referrals (referrer_id, referee_id, bonus_days, used, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (referrer_id, referee_id, 1, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def give_referral_bonus(referrer_id):
    user = get_user(referrer_id)
    if user:
        expire = datetime.strptime(user[4], "%Y-%m-%d %H:%M:%S") if user[4] else datetime.now()
        new_expire = expire + timedelta(days=1)
        update_subscription(referrer_id, expire_date=new_expire)
