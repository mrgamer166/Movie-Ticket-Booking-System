from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

SEAT_PRICES = {
    "regular": 150,
    "balcony": 250,
    "premium": 400
}

# -----------------------------
# DB Connection
# -----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


# -----------------------------
# Get Movies
# -----------------------------
def get_all_movies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()

    conn.close()
    return movies


# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))


# -----------------------------
# Register
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return render_template("register.html", error="Email already exists")

        try:
            cursor.execute(
                "INSERT INTO users (name, username, email, password) VALUES (%s,%s,%s,%s)",
                (name,username, email, password)
            )
            conn.commit()
        except:
            return render_template("register.html", error="Username already exists")

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html", error=error)


# -----------------------------
# Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s",
            (username, username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = user[2]   # username
            session["name"] = user[1]       # name
            return redirect(url_for("movies"))
        else:
            error = "Invalid credentials"
    
    return render_template("login.html", error=error)


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -----------------------------
# Movies Page
# -----------------------------
@app.route("/movies")
def movies():
    if "username" not in session:
        return redirect(url_for("login"))

    movies = get_all_movies()
    return render_template("movies.html", movies=movies)

# -----------------------------
# Payment
# -----------------------------
@app.route("/payment", methods=["POST"])
def payment():

    if "username" not in session:
        return redirect(url_for("login"))

    seats = request.form["seats"].split(",")
    movie_id = request.form["movie_id"]

    total = 0
    seat_types = []

    for seat in seats:
        row = seat[0]

        if row in ['A','B','C']:
            price = SEAT_PRICES["regular"]
            seat_types.append("Regular")
        elif row in ['D','E','F','G']:
            price = SEAT_PRICES["balcony"]
            seat_types.append("Balcony")
        else:
            price = SEAT_PRICES["premium"]
            seat_types.append("Premium")

        total += price

    return render_template(
        "payment.html",
        seats=seats,
        total=total,
        movie_id=movie_id
    )

# -----------------------------
# Admin Page
# -----------------------------
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    movies = get_all_movies()
    return render_template("admin.html", movies=movies)


# -----------------------------
# Admin Login
# -----------------------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid admin credentials"

    return render_template("admin_login.html", error=error)


# -----------------------------
# ADD MOVIE (WITH IMAGE)
# -----------------------------
@app.route("/add-movie", methods=["POST"])
def add_movie():

    name = request.form["name"]
    genre = request.form["genre"]
    duration = request.form["duration"]

    file = request.files["poster"]

    filename = ""
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO movies (name, genre, duration, poster) VALUES (%s,%s,%s,%s)",
        (name, genre, duration, filename)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# -----------------------------
# DELETE MOVIE
# -----------------------------
@app.route("/delete-movie/<int:id>")
def delete_movie(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    # delete bookings FIRST
    cursor.execute("DELETE FROM bookings WHERE movie_id=%s", (id,))

    # then delete movie
    cursor.execute("DELETE FROM movies WHERE id=%s", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

# -----------------------------
# Admin booking
# -----------------------------

@app.route("/admin-bookings")
def admin_bookings_list():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # get all movies
    cursor.execute("""
    SELECT m.id, m.name, m.genre, m.duration, m.poster,
    COUNT(b.id) as total
    FROM movies m
    LEFT JOIN bookings b ON m.id = b.movie_id
    GROUP BY m.id
    """)
    movies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_booking_list.html", movies=movies)

@app.route("/admin-bookings/<int:movie_id>")
def admin_bookings(movie_id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT seat_number, username FROM bookings WHERE movie_id=%s"
    cursor.execute(query, (movie_id,))
    data = cursor.fetchall()

    booked_seats = [x[0] for x in data]
    seat_users = {x[0]: x[1] for x in data}

    cursor.close()
    conn.close()

    return render_template(
        "admin_bookings.html",
        booked_seats=booked_seats,
        seat_users=seat_users
    )

# -----------------------------
# Seat view
# -----------------------------

@app.route("/admin-bookings/<int:movie_id>")
def admin_booking_view(movie_id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT seat_number, username 
    FROM bookings 
    WHERE movie_id=%s
    """
    cursor.execute(query, (movie_id,))
    booked = cursor.fetchall()

    conn.close()

    booked_dict = {b["seat_number"]: b["username"] for b in booked}

    return render_template(
        "admin_seats.html",
        booked_dict=booked_dict
    )

# -----------------------------
# EDIT MOVIE
# -----------------------------
@app.route("/edit-movie/<int:id>", methods=["POST"])
def edit_movie(id):

    name = request.form["name"]
    genre = request.form["genre"]
    duration = request.form["duration"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE movies SET name=%s, genre=%s, duration=%s WHERE id=%s",
        (name, genre, duration, id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# -----------------------------
# Booking
# -----------------------------
@app.route("/book/<int:movie_id>")
def book(movie_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT seat_number, username FROM bookings WHERE movie_id=%s"
    cursor.execute(query, (movie_id,))
    booked = cursor.fetchall()

    booked_seats = [seat[0] for seat in booked]

    # 🔥 NEW: map seat → user
    seat_users = {seat[0]: seat[1] for seat in booked}

    conn.close()

    return render_template(
        "book.html",
        movie_id=movie_id,
        booked_seats=booked_seats,
        seat_users=seat_users
    )


@app.route("/confirm-booking", methods=["POST"])
def confirm_booking():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    movie_id = request.form["movie_id"]
    seats = request.form["seats"].split(",")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for seat in seats:
            query = "INSERT INTO bookings (username, movie_id, seat_number) VALUES (%s,%s,%s)"
            cursor.execute(query, (username, movie_id, seat))
        conn.commit()

    except:
        return "Some seats already booked!"

    cursor.close()
    conn.close()

    return redirect(url_for("book", movie_id=movie_id))

# -----------------------------
# My booking
# -----------------------------
@app.route("/my-bookings")
def my_bookings():

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        MIN(bookings.id) as id,
        movies.name,
        GROUP_CONCAT(bookings.seat_number ORDER BY bookings.seat_number) as seats,
        DATE_FORMAT(bookings.booking_time, '%Y-%m-%d %H:%i') as time
    FROM bookings
    JOIN movies ON bookings.movie_id = movies.id
    WHERE bookings.username = %s
    GROUP BY movies.name, bookings.booking_time
    ORDER BY bookings.booking_time DESC
    """

    cursor.execute(query, (username,))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("my_bookings.html", bookings=data)

# -----------------------------
# Seat cancelation
# -----------------------------
@app.route("/cancel-booking/<int:booking_id>")
def cancel_booking(booking_id):

    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # delete ALL seats from that booking group
    cursor.execute("""
        DELETE FROM bookings
        WHERE id >= %s
        AND id <= %s + 10
    """, (booking_id, booking_id))  # simple grouping logic

    conn.commit()
    conn.close()

    return redirect(url_for("my_bookings"))

# -----------------------------
# Username Checker
# -----------------------------
@app.route("/check-username")
def check_username():

    username = request.args.get("username")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()

    conn.close()

    return jsonify({"available": not bool(user)})


if __name__ == "__main__":
    app.run(debug=True)