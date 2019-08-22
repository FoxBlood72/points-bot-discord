import sqlite3
from datetime import datetime
import time

def get_conn():
    conn = sqlite3.connect('discodatabase.db')
    cur = conn.cursor()
    return conn, cur


def check_user(username_id):
    t = (username_id, )
    conn, cur = get_conn()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = ?",t)
    users = cur.fetchall()
    if(users[0][0] == 0):
        return False
    else:
        return True
    
def add_user(username_id):
    conn, cur = get_conn()
    t = (username_id, 0, )
    cur.execute("INSERT INTO users(username, points) VALUES(?,?)", t)
    conn.commit()
    
def add_points_user(username_id, points):
    conn, cur = get_conn()
    t = (points, username_id, )
    cur.execute("UPDATE users SET points = points + ? WHERE username = ?", t)
    conn.commit()


def remove_points(username_id, points):
    conn, cur = get_conn()
    t = (points, username_id, )
    t2 = (username_id, )
    cur.execute("UPDATE users SET points = points - ? WHERE username = ?", t)
    cur.execute("UPDATE users SET points = 0 WHERE username = ? AND points < 0", t2)
    conn.commit()


def add_points(username_id, points):
    t = (username_id, )
    if(check_user(username_id) == False and username_id.isdigit()):
        add_user(username_id)
        add_points_user(username_id,points)
    elif(username_id.isdigit()):
        add_points_user(username_id,points)
       

def add_leaderboard(username, message_id, count):
    conn, cur = get_conn()
    now=datetime.now()
    timestamp=datetime.timestamp(now)
    t = (username, message_id, timestamp, 1, count, )
    cur.execute("INSERT INTO board_tables(username, message_id, created_time, page_number, last_usernumber) VALUES(?,?,?,?,?)", t)
    conn.commit()
    
def check_leaderboard(message_id, user_id):
    conn, cur = get_conn()
    t = (user_id, message_id, )
    cur.execute("SELECT COUNT(*) FROM board_tables WHERE username = ? AND message_id = ?",t)
    data = cur.fetchall()
    if(data[0][0] == 0):
        return False
    else:
        return True
    
    
def get_user_point(username_id):
    conn, cur = get_conn()
    t = (username_id, )
    cur.execute("SELECT * FROM users WHERE username = ?", t)
    data = cur.fetchall()
    if not data:
        return 0
    else:
        return data[0][2]
    
def get_leaderboard_page(message_id, user_id):
    conn, cur = get_conn()
    t = (user_id, message_id, )
    cur.execute("SELECT * FROM board_tables WHERE username = ? AND message_id = ?",t)
    data = cur.fetchall()
    return data[0][4], data[0][5]
    
def update_leaderboard(page, last_user, message_id):
    conn, cur = get_conn()
    t = (page, last_user, message_id)
    cur.execute("UPDATE board_tables SET page_number = ? , last_usernumber = ? WHERE message_id = ?", t)
    conn.commit()
    
def get_users(page = 1):
    page_offset = (page - 1) * 10
    conn, cur = get_conn()
    cur.execute("SELECT * FROM users ORDER BY points DESC LIMIT "+ str(page_offset) +",10")
    rows = cur.fetchall()
    return rows
    
    
def insert_points_requests(message_id, users, points, approved, created_by):
    conn, cur = get_conn()
    t = (message_id, users, points, approved, created_by, )
    cur.execute("INSERT INTO points_requests(message_id, users, points, approved, created_by)  VALUES(?,?,?,?,?)", t)
    conn.commit()
    
    
def check_requests(message_id):
    conn, cur = get_conn()
    t = (message_id, )
    cur.execute("SELECT * FROM points_requests WHERE message_id = ? AND approved = 0 LIMIT 1", t)
    data = cur.fetchall()
    if(not data):
        return None
    else:
        return True
        
        
def get_users_requests(message_id):
    conn, cur = get_conn()
    t = (message_id, )
    cur.execute("SELECT * FROM points_requests WHERE message_id = ? LIMIT 1", t)
    data = cur.fetchall()
    if(not data):
        return None
    else:
        return data[0][2], data[0][3]
        
def update_requests(message_id, app):
    conn, cur = get_conn()
    t = (app, message_id, )
    cur.execute("UPDATE points_requests SET approved = ? WHERE message_id = ?", t)
    conn.commit()
    
    
async def reset_database():
    conn, cur = get_conn()
    cur.execute("DELETE FROM users WHERE 'a' = 'a'")
    conn.commit()