from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

app = Flask(__name__)
app.secret_key = "supersecretkey"


# -----------------------------
# Database Connection
# -----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# -----------------------------
# Home Route
# -----------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))


# -----------------------------
# Register Route
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    error = None

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if len(password) < 8:
            error = "Password must be at least 8 characters long"
            return render_template("register.html", error=error)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE email=%s"
        cursor.execute(query, (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = "Account with this email already exists"
            cursor.close()
            conn.close()
            return render_template("register.html", error=error)

        try:
            query = "INSERT INTO users (username, email, password) VALUES (%s,%s,%s)"
            cursor.execute(query, (username, email, password))
            conn.commit()

        except mysql.connector.IntegrityError:
            error = "Username already exists"
            cursor.close()
            conn.close()
            return render_template("register.html", error=error)

        cursor.close()
        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html", error=error)


# -----------------------------
# Login Route
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s"
        cursor.execute(query, (username, username, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("movies"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

# -----------------------------
# Logout Route
# -----------------------------

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("admin", None)
    return redirect(url_for("login"))

# -----------------------------
# Movies Page
# -----------------------------
@app.route("/movies")
def movies():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("movies.html")


# -----------------------------
# Admin Page
# -----------------------------
@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    return render_template("admin.html")
# -----------------------------
# Admin Login Page
# -----------------------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():

    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # simple admin credentials
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid admin credentials"

    return render_template("admin_login.html", error=error)

# -----------------------------
# Seat booking page
# -----------------------------

@app.route("/book/<int:movie_id>")
def book(movie_id):

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # get already booked seats
    query = "SELECT seat_number FROM bookings WHERE movie_id=%s"
    cursor.execute(query, (movie_id,))
    booked = cursor.fetchall()

    cursor.close()
    conn.close()

    # convert [('A1',), ('B2',)] → ['A1','B2']
    booked_seats = [seat[0] for seat in booked]

    return render_template("book.html",movie_id=movie_id,booked_seats=booked_seats)

# -----------------------------
# Confirm seat booking
# -----------------------------

@app.route("/confirm-booking", methods=["POST"])
def confirm_booking():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    movie_id = request.form["movie_id"]
    seat = request.form["seat"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO bookings (username, movie_id, seat_number) VALUES (%s,%s,%s)"
        cursor.execute(query, (username, movie_id, seat))
        conn.commit()

    except:
        return "Seat already booked!"

    cursor.close()
    conn.close()

    return "Booking Successful!"

# -----------------------------
# Username Checker
# -----------------------------

@app.route("/check-username")
def check_username():

    username = request.args.get("username")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username=%s"
    cursor.execute(query, (username,))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({"available": False})
    else:
        return jsonify({"available": True})

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)