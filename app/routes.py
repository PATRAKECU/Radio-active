from flask import render_template, request, redirect, url_for, session, Response, current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from app.forms import DecayForm, RegisterForm, LoginForm, EditSimulationForm, ChangePasswordForm
import math
import sqlite3
from app.plot import generate_decay_plot, generate_decay_plot_image
from functools import wraps
import logging
from weasyprint import HTML
from datetime import datetime
import os


# Debug configuration for user information
logging.basicConfig(level=logging.DEBUG)

# Connect to database in SQLite3
def get_db_connection():
    conn = sqlite3.connect("radioactive.db")
    # Enable dictionary-style access to columns
    conn.row_factory = sqlite3.Row
    return conn

# Establish function to require uses to login to access certain services
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# Prevent caching of sensitive data in shared or public browsers
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    # Use validations from the form in forms.py
    form = LoginForm()    

    if form.validate_on_submit():
        # Clear the session after the form has been validated
        session.clear()
        username = form.username.data
        password = form.password.data        

        # Find the user in the database
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE name = ?", (username,)).fetchone()
        conn.close()

        # Assess matching for debugging purpuses
        logging.debug(f"Username: {username}")
        logging.debug(f"User found: {user is not None}")
        if user:
            logging.debug(f"Password match: {check_password_hash(user['password'], password)}")

        # Manage errors of user input
        if user is None or not check_password_hash(user["password"], password):
            form.username.errors.append("Invalid username or password.")
            return render_template("login.html", form=form)

        # Provide a username with a session
        session["user_id"] = user["id"]
        session["username"] = user["name"]
        return redirect(url_for("index"))

    # If the data is invalid, redirect user to login
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    # Use validations from the form in forms.py
    form = RegisterForm()

    if form.validate_on_submit():
        # Obtain data from user if form is validated
        username = form.username.data
        password = form.password.data
        # Generate hash for password
        hashed_password = generate_password_hash(password)

        # Try adding data to the database
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                         # Use email placeholder for demonstration purposes
                         (username, f"{username}@example.com", hashed_password))
            conn.commit()
            conn.close()
            # If successful, redirect user to login
            return redirect(url_for("login"))
        # Manage error if username already exists
        except sqlite3.IntegrityError:
            form.username.errors.append("Username already exists.")

    # If unsuccessful, redirect user to the register form
    return render_template("register.html", form=form)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    # Use validations from the form in forms.py
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Extract current and new password from validated form
        current = form.current_password.data
        new = form.new_password.data

        # Retrieve current user using session ID
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

        # If current password does not match hash in database, show error
        if not check_password_hash(user["password"], current):
            form.current_password.errors.append("Incorrect current password.")
            conn.close()
            # Redirect user to change_password.html if unsuccessful
            return render_template("change_password.html", form=form)

        #Generate new hash
        new_hash = generate_password_hash(new)
        # Update database with new hash
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, session["user_id"]))
        conn.commit()
        conn.close()

        # Password change confirmed, return to main page
        return redirect(url_for("index"))

    # Render change_password.html with form and errors if validation fails
    return render_template("change_password.html", form=form)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Use validations from the form in forms.py
    form = DecayForm()

    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Populate element choices dynamically from database
    cursor.execute("SELECT id, name FROM elements ORDER BY name")
    elements = cursor.fetchall()
    form.element.choices = [(row["id"], row["name"]) for row in elements]

    if form.validate_on_submit():
        # Obtain data from user if form is validated
        n0 = form.n0.data
        t = form.t.data
        element_id = form.element.data

        # Fetch half-life and units for selected element
        cursor.execute("SELECT name, half_life, unit, quantity_unit FROM elements WHERE id = ?", (element_id,))
        element = cursor.fetchone()
        if element is None:
            conn.close()
            # Show error if element is not found
            return render_template("index.html", form=form, error="Element not found.")

        # Calculate the decay constant
        lam = math.log(2) / element["half_life"]
        lam_str = "%.5e" % lam
        # Calculate the remaining quantity with mathematical model
        nt = n0 * math.exp(-lam * t)
        # Build the Plotly plot calling the generate_decay_plot function
        plot_html = generate_decay_plot(n0, lam, t_max=int(t * 1.5))
        # Obtain current time and date
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save simulation in database automatically
        cursor.execute("""
            INSERT INTO simulations (user_id, element_id, name, n0, t, nt, half_life, unit, quantity_unit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            element_id,
            element["name"],
            n0,
            t,
            nt,
            element["half_life"],
            element["unit"],
            element["quantity_unit"],
            timestamp
        ))
        conn.commit()
        conn.close()

        # Pass data to template
        return render_template("result.html", n0=n0, t=t,
                               half_life=element["half_life"],
                               nt=nt, lam_str=lam_str, plot_html=plot_html,
                               unit=element["unit"], quantity_unit=element["quantity_unit"], name=element["name"],
                               timestamp=timestamp)

    conn.close()
    # Render index.html with form and errors if validation fails
    return render_template("index.html", form=form)    


@app.route("/history")
@login_required
def history():

    # Establish connection with database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch data from simulations' table and order it by newest to oldest
    # Filter simulations by current user and sort by timestamp descending
    cursor.execute("""
        SELECT * FROM simulations
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (session["user_id"],))

    rows = cursor.fetchall()
    conn.close()

    # Render template showing fetched data in a table
    return render_template("history.html", rows=rows)


@app.route("/simulation/<int:sim_id>")
@login_required
def simulation_detail(sim_id):
    # Pass the simulation id to the function

    # Establish connection with database
    conn = get_db_connection()
    
    # Join simulations and elements tables to enrich simulation data
    # Filter by sim_id and user_id to enforce access control    
    row = conn.execute("""
        SELECT s.*, e.name AS element_name, e.half_life, e.unit, e.quantity_unit
        FROM simulations s
        JOIN elements e ON s.element_id = e.id
        WHERE s.id = ? AND s.user_id = ?                                              
    """, (sim_id, session["user_id"])).fetchone()
    conn.close()

    # Redirect user to history if the simulation doesn't exist
    # Prevent access to invalid or unauthorized simulation IDs
    if row is None:
        return redirect(url_for("history"))    
    
    # Calculate the decay constant
        # λ = ln(2) / t½
    lam = math.log(2) / row["half_life"]
    # Use scientific notation to manage very small values of the decay constant
    lam_str = "%.5e" % lam
    # Obtain the remaining quantity from the database
    # Format for display with 5 decimals
    nt_str = "%.5f" % row["nt"]
    
    # Build the Plotly plot calling the generate_decay_plot function
    plot_html = generate_decay_plot(row["n0"], lam, t_max=int(row["t"] * 1.5))

    # Pass all relevant data and formatted values to template
    # Render the simulation detail in it's template
    return render_template("simulation_detail.html", row=row, plot_html=plot_html,
                           lam_str=lam_str, nt_str=nt_str,
                           unit=row["unit"], quantity_unit=row["quantity_unit"])


@app.route("/simulation/<int:sim_id>/edit", methods=["GET", "POST"])
@login_required
def edit_simulation(sim_id):

    # Validate data with the form in forms.py
    form = EditSimulationForm()

    # Establish connection with database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load elements for dropdown ordered by name
    cursor.execute("SELECT id, name FROM elements ORDER BY name")
    form.element.choices = [(row["id"], row["name"]) for row in cursor.fetchall()]

    # Get simulation filtered by sim_id and user_id
    row = cursor.execute("""
        SELECT * FROM simulations WHERE id = ? AND user_id = ?
    """, (sim_id, session["user_id"])).fetchone()

    # If simulation doesn't exist, redirect user to history
    if row is None:
        conn.close()
        return redirect(url_for("history"))

    # Prepopulate the form with previous data
    if request.method == "GET":
        form.element.data = row["element_id"]
        form.n0.data = row["n0"]
        form.t.data = row["t"]

    # Obtain new data from the user after validation
    if form.validate_on_submit():
        element_id = form.element.data
        n0 = form.n0.data
        t = form.t.data

        # Obtain elemet's half-life filtered by id
        cursor.execute("SELECT half_life FROM elements WHERE id = ?", (element_id,))
        element = cursor.fetchone()
        # Render edit_simulation.html template if element is not found and show error
        if element is None:
            conn.close()
            return render_template("edit_simulation.html", form=form, error="Element not found.")

        # Calculate decay constant
        lam = math.log(2) / element["half_life"]
        # Calculate remaining quantity from mathematical model
        nt = n0 * math.exp(-lam * t)
        # Obtain current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update edited simulation in database filtered by id and user_id
        cursor.execute("""
            UPDATE simulations
            SET element_id = ?, n0 = ?, t = ?, nt = ?, timestamp = ?
            WHERE id = ? AND user_id = ?
        """, (element_id, n0, t, nt, timestamp, sim_id, session["user_id"]))
        conn.commit()
        conn.close()

        # Show edited simulation detail to user
        return redirect(url_for("simulation_detail", sim_id=sim_id))
    
    # Close connection to database
    conn.close()
    # If data entered is invalid, render edit_simulation.html again
    return render_template("edit_simulation.html", form=form, sim_id=sim_id)


@app.route("/element/<int:element_id>/units")
@login_required
def get_element_units(element_id):
    # Pass element_id 

    # Connect to database    
    conn = get_db_connection()

    # Query the units of time and quantity for the selected element
    row = conn.execute("""
        SELECT unit, quantity_unit FROM elements WHERE id = ?
    """, (element_id,)).fetchone()
    conn.close()

    # If the element exists, return its units as a JSON dictionary 
    if row:
        return {"unit": row["unit"], "quantity_unit": row["quantity_unit"]}
    
    # If the element is not found, return empty strings
    return {"unit": "", "quantity_unit": ""}


@app.route("/simulation/<int:sim_id>/export")
@login_required
def export_simulation_pdf(sim_id):
    # Pass the simulation id

    # Connect to database
    conn = get_db_connection()
    
    # Retrieve simulation and element data, enforcing access control
    row = conn.execute("""
        SELECT s.*, e.name AS element_name, e.half_life, e.unit, e.quantity_unit
        FROM simulations s
        JOIN elements e ON s.element_id = e.id
        WHERE s.id = ? AND s.user_id = ?
    """, (sim_id, session["user_id"])).fetchone()
    conn.close()

    # Redirect the user to history if the simulation is not found
    if row is None:
        return redirect(url_for("history"))

    # Calculate decay constant and format for display
    lam = math.log(2) / row["half_life"]
    lam_str = "%.5e" % lam
    # Format remaining quantity for display
    nt_str = "%.5f" % row["nt"]
    # Generate static decay plot and verify file access
    plot_path = generate_decay_plot_image(row["n0"], lam, t_max=int(row["t"] * 1.5))
    assert os.path.exists(plot_path)
    assert os.access(plot_path, os.R_OK)

    # Define base URL and relative path for PDF rendering
    project_root = os.path.abspath(os.path.join(app.root_path, ".."))
    rel_path = os.path.relpath(plot_path, start=project_root).replace(os.path.sep, '/')
    base_url = f'file:///{project_root.replace(os.path.sep, "/")}/'
    
    # Render HTML template with simulation data
    html = render_template(
        "pdf_exp.html",
        row=row,
        lam_str=lam_str,
        nt_str=nt_str,
        plot_path=rel_path
    )
    
    # Generate PDF from rendered HTML
    pdf = HTML(string=html, base_url=base_url).write_pdf()

    # Return PDF as HTTP response to be opened in browser
    return Response(pdf, mimetype="application/pdf", headers={
        "Content-Disposition": f"inline; filename=simulation_{sim_id}.pdf"
    })
