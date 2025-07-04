from flask import Flask, render_template, request, redirect, session, flash, url_for
import hashlib
import uuid

app = Flask(__name__)
# IMPORTANT: In a real app, use a strong, environment-variable based secret key
app.secret_key = 'your_very_secret_key_here_please_change_this_for_production'

# -------- Mock Data --------
mock_users = {}  # Stores email: hashed_password
mock_bookings = []  # Stores booking dictionaries

# -------- Helper Functions --------
def hash_password(password):
    """Hashes a given password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def send_mock_email(email, booking_info):
    """Mocks sending a confirmation email for a booking."""
    print(f"[MOCK EMAIL] Sent to {email}:\nBooking confirmed for {booking_info['movie']}\n"
          f"Seat: {booking_info['seat']}, Date: {booking_info['date']}, Time: {booking_info['time']}\n"
          f"Booking ID: {booking_info['id']}\n")

# -------- Routes --------
@app.route('/')
def index():
    """Renders the initial landing page.
       You might want to redirect to '/home' directly if index.html is not a separate landing page."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in mock_users:
            flash("Account already exists. Please login.", "error") # Added category for styling
            return redirect(url_for('login'))

        mock_users[email] = hash_password(password)
        flash("Account created! Please login.", "success") # Added category for styling
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed = hash_password(password)

        if email in mock_users and mock_users[email] == hashed:
            session['user'] = email
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password.", "error")
    return render_template('login.html')

@app.route('/home')
def home():
    """
    Renders the main movie listing page.
    Passes 'now showing' and 'coming soon' movie data to the template.
    """
    if 'user' not in session:
        flash("Please log in to view movies.", "info")
        return redirect(url_for('login'))

    # --- FIX: Updated movie data structure to use 'poster_filename' ---
    # These 'poster_filename' values must exactly match your image file names
    # located in your 'static/images/' directory.
    movies = [
        {'title': '8 Vasantalu', 'genre': 'UA16+ • Telugu', 'poster_filename': '8 vasantalu.jpeg'}, #
        {'title': 'From the World of John Wick: Ballerina', 'genre': 'A • Telugu', 'poster_filename': 'from the world.jpeg'}, #
        {'title': 'Sitaare Zameen Par', 'genre': 'UA13+ • Telugu, Hindi', 'poster_filename': 'sitaare zameen par.jpeg'}, #
        {'title': 'How to Train Your Dragon', 'genre': 'UA7+ • English', 'poster_filename': 'dragon.jpeg'}, #
        {'title': 'Kuberaa', 'genre': 'UA13+ • Telugu, Tamil', 'poster_filename': 'kubera.jpeg'}, #
        {'title': 'Bhairavam', 'genre': 'A • Telugu', 'poster_filename': 'bhairavam.jpeg'}, #
    ]

    coming_soon_movies = [
        {'title': '28 Years Later', 'genre': 'A • English', 'poster_filename': '28years.jpeg'}, #
        {'title': 'Elio', 'genre': 'U • English', 'poster_filename': 'elio.jpeg'}, #
    ]

    return render_template('home.html', user=session['user'], movies=movies, coming_soon_movies=coming_soon_movies)

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    """
    Handles movie booking form display and submission.
    Expects 'movie_title' as a URL query parameter for GET requests (from home.html).
    """
    if 'user' not in session:
        flash("Please log in to book tickets.", "info")
        return redirect(url_for('login'))

    # Get movie title from URL query parameter (e.g., /booking?movie_title=MovieName)
    movie_title = request.args.get('movie_title', 'Example Movie')

    if request.method == 'POST':
        # Store booking details in session temporarily before payment
        session['pending_booking'] = {
            'movie': request.form.get('movie_title_hidden', 'Unknown Movie'), # Get from hidden input in booking_form.html
            'seat': request.form['seat'],
            'date': request.form['date'],
            'time': request.form['time']
        }
        return redirect(url_for('payment'))

    # For GET request, render the booking form with the movie title
    return render_template('booking_form.html', movie=movie_title)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    """Handles the payment process (mock) and confirms booking."""
    if 'user' not in session or 'pending_booking' not in session:
        flash("No booking details found. Please select a movie first.", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Simulate payment processing
        booking_info = session['pending_booking']
        booking_info['user'] = session['user']
        booking_info['id'] = str(uuid.uuid4())[:8] # Generate a short unique booking ID

        mock_bookings.append(booking_info) # Store booking in mock data
        session['last_booking'] = booking_info # Store for confirmation page
        send_mock_email(session['user'], booking_info) # Simulate sending email
        session.pop('pending_booking', None) # Clear pending booking from session
        flash("Payment successful. Ticket booked!", "success")

        return redirect(url_for('confirmation'))

    # For GET request, render payment page, showing pending booking details
    return render_template('payment.html', pending_booking=session['pending_booking'])

@app.route('/confirmation')
def confirmation():
    """Displays booking confirmation details."""
    if 'user' not in session or 'last_booking' not in session:
        flash("No recent booking to confirm.", "info")
        return redirect(url_for('home'))

    booking = session['last_booking']
    return render_template('confirmation.html', booking=booking)

@app.route('/logout')
def logout():
    """Logs out the current user by clearing the session."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# 🔍 Debug Route: View all mock bookings
@app.route('/debug/bookings')
def debug_bookings():
    """Debug route to view all mock bookings."""
    if not mock_bookings:
        return "No bookings yet."

    html = "<h2>All Bookings</h2><ul>"
    for b in mock_bookings:
        html += f"<li><b>User:</b> {b['user']}, <b>Movie:</b> {b['movie']}, <b>Seat:</b> {b['seat']}, <b>Date:</b> {b['date']}, <b>Time:</b> {b['time']}, <b>ID:</b> {b['id']}</li>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    print("🚀 Mock MovieMagic running at http://127.0.0.1:5000")
    app.run(debug=True) # Run in debug mode for development