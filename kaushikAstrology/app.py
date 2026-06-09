from flask import Flask, render_template, request, redirect, url_for, session
from config import *
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Database Setup
def init_db():
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        dob TEXT NOT NULL,
        birth_time TEXT NOT NULL,
        birth_place TEXT NOT NULL,
        service TEXT NOT NULL,
        booking_time TEXT NOT NULL,
       payment_status TEXT DEFAULT 'Pending',
       is_new INTEGER DEFAULT 1,
       is_active INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()

# Create database
init_db()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        name = request.form.get("name")
        phone = request.form.get("phone")
        dob = request.form.get("dob")
        birth_time = request.form.get("birth_time")
        birth_place = request.form.get("birth_place")
        service = request.form.get("service")

        # 🔴 MOBILE VALIDATION
        if not phone or not phone.isdigit() or len(phone) != 10:
            return "Invalid Mobile Number! Only 10 digit number allowed"

        booking_time = datetime.now().strftime(
            "%d/%m/%Y %I:%M:%S %p"
        )

        conn = sqlite3.connect("bookings.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO bookings
        (
            name,
            phone,
            dob,
            birth_time,
            birth_place,
            service,
            booking_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            phone,
            dob,
            birth_time,
            birth_place,
            service,
            booking_time
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("success"))

    return render_template("index.html")# YAHAN SE LOGIN ROUTE ADD KARO

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect(url_for("admin"))

    return render_template("login.html")

    # YAHAN LOGOUT ROUTE LAGAO

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(url_for("login"))
@app.route("/archive/<int:id>")
def archive_booking(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE bookings SET is_active = 0 WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

@app.route("/archived")
def archived():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM bookings WHERE is_active = 0 ORDER BY id DESC"
    )

    bookings = cur.fetchall()

    conn.close()

    return str(bookings)

@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM bookings")
    booking_count = cur.fetchone()[0]

    cur.execute("SELECT * FROM bookings WHERE is_active = 1 ORDER BY id DESC")
    bookings = cur.fetchall()

    conn.close()

    html = """
    <html>
    <head>

        <meta http-equiv="refresh" content="10">
        <title>Admin Panel</title>
        <style>
            body{
                font-family:Arial;
                padding:20px;
                background:#f5f5f5;
            }

            h1{
                text-align:center;
            }

            table{
                width:100%;
                border-collapse:collapse;
                background:white;
            }

            th{
                background:#0B1F3A;
                color:white;
            }

            th,td{
                border:1px solid #ddd;
                padding:10px;
                text-align:center;
            }

            tr:nth-child(even){
                background:#f2f2f2;
            }
        </style>
    </head>

    <body>

    <h1>All Bookings</h1>
    <div style="text-align:right;margin-bottom:15px;">
    <a href="/logout"
       style="
       background:red;
       color:white;
       padding:10px 15px;
       text-decoration:none;
       border-radius:5px;
       font-weight:bold;
       ">
       Logout
    </a>
</div>

<div style="
background:#FFD700;
padding:12px;
margin-bottom:20px;
border-radius:10px;
font-size:22px;
font-weight:bold;
text-align:center;
">
🔔 Total Bookings: """ + str(booking_count) + """
</div>

    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Phone</th>
            <th>Date Of Birth</th>
            <th>Birth Time</th>
            <th>Birth Place</th>
            <th>Service</th>
            <th>Booking Time</th>
            <th>Action</th>
        </tr>
    """

    for booking in bookings:

        html += f"""
        <tr>
            <td>{booking[0]}</td>
            <td>{booking[1]}</td>
            <td>{booking[2]}</td>
            <td>{booking[3]}</td>
            <td>{booking[4]}</td>
            <td>{booking[5]}</td>
            <td>{booking[6]}</td>
            <td>{booking[7]}</td>
            <td>
            <a href="/archive/{booking[0]}">Archive</a>
            </td>
        </tr>
        """

    html += """
    </table>

    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    app.run(debug=True)