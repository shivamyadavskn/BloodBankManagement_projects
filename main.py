import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime

app = Flask(__name__)
conn = psycopg2.connect(
    host="dpg-choafmg2qv295pruiqe0-a.oregon-postgres.render.com",
    database="alchemy_zyif",
    user="accounts",
    password="BPqY8JN9DAufCtYdBDbi3qo815EKdqwi"
)
app.secret_key = 'your_secret_key'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
        conn.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user and user[2] == password:
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password. Please try again.')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear();
    flash('Logged out successfully!')
    return redirect(url_for('home'))


@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        blood_type = request.form['blood_type']
        availability = True if 'availability' in request.form else False

        cur = conn.cursor()
        cur.execute("INSERT INTO donors (name, contact, blood_type, availability) VALUES (%s, %s, %s, %s)",
                    (name, contact, blood_type, availability))
        conn.commit()

        flash('Donor added successfully!')
        return redirect(url_for('donor_list'))

    return render_template('add_donor.html')


@app.route('/donor_list')
def donor_list():
    cur = conn.cursor()
    cur.execute("SELECT * FROM donors")
    donors = cur.fetchall()
    return render_template('donor_list.html', donors=donors)


@app.route('/edit_donor/<int:donor_id>', methods=['GET', 'POST'])
def edit_donor(donor_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM donors WHERE id = %s", (donor_id,))
    donor = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        blood_type = request.form['blood_type']
        availability = True if 'availability' in request.form else False

        cur.execute("UPDATE donors SET name = %s, contact = %s, blood_type = %s, availability = %s WHERE id = %s",
                    (name, contact, blood_type, availability, donor_id))
        conn.commit()

        flash('Donor information updated successfully!')
        return redirect(url_for('donor_list'))

    return render_template('edit_donor.html', donor=donor)


@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']

        cur = conn.cursor()
        cur.execute("INSERT INTO staff (name, position, department) VALUES (%s, %s, %s)",
                    (name, position, department))
        conn.commit()

        flash('Staff added successfully!')
        return redirect(url_for('staff_list'))

    return render_template('add_staff.html')


@app.route('/staff_list')
def staff_list():
    cur = conn.cursor()
    cur.execute("SELECT * FROM staff")
    staff = cur.fetchall()
    return render_template('staff_list.html', staff=staff)


@app.route('/edit_staff/<int:staff_id>', methods=['GET', 'POST'])
def edit_staff(staff_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM staff WHERE id = %s", (staff_id,))
    staff = cur.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        department = request.form['department']

        cur.execute("UPDATE staff SET name = %s, position = %s, department = %s WHERE id = %s",
                    (name, position, department, staff_id))
        conn.commit()

        flash('Staff information updated successfully!')
        return redirect(url_for('staff_list'))

    return render_template('edit_staff.html', staff=staff)


@app.route('/add_blood_unit', methods=['GET', 'POST'])
def add_blood_unit():
    if request.method == 'POST':
        blood_type = request.form['blood_type']
        quantity = request.form['quantity']
        expiration_date = request.form['expiration_date']
        storage_location = request.form['storage_location']

        cur = conn.cursor()
        cur.execute(
            "INSERT INTO blood_units (blood_type, quantity, storage_location, expiration_date) VALUES (%s, %s, %s, %s)",
            (blood_type, quantity, storage_location, expiration_date))
        conn.commit()

        flash('Blood unit added successfully!')
        return redirect(url_for('blood_inventory'))

    return render_template('add_blood_unit.html')


@app.route('/blood_inventory')
def blood_inventory():
    cur = conn.cursor()
    cur.execute("SELECT * FROM blood_units")
    blood_units = cur.fetchall()
    return render_template('blood_inventory.html', blood_units=blood_units)


@app.route('/request_blood', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        blood_type = request.form['blood_type']
        quantity = request.form['quantity']
        location = request.form['location']
        request_date = datetime.now()

        cur = conn.cursor()
        cur.execute("INSERT INTO blood_requests (blood_type, quantity, location) VALUES (%s, %s, %s)",
                    (blood_type, quantity, location))
        conn.commit()

        flash('Blood request sent successfully!')
        return redirect(url_for('blood_requests'))

    return render_template('request_blood.html')


@app.route('/blood_requests')
def blood_requests():
    cur = conn.cursor()
    cur.execute("SELECT * FROM blood_requests")
    blood_requests = cur.fetchall()
    return render_template('blood_requests.html', blood_requests=blood_requests)


@app.route('/schedule_appointment', methods=['GET', 'POST'])
def schedule_appointment():
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        status = 'Scheduled'

        cur = conn.cursor()
        cur.execute("INSERT INTO appointments (date, time, status) VALUES (%s, %s, %s)",
                    (date, time, status))
        conn.commit()

        flash('Appointment scheduled successfully!')
        return redirect(url_for('appointments'))

    return render_template('schedule_appointment.html')


@app.route('/appointments')
def appointments():
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments")
    appointments = cur.fetchall()
    return render_template('appointments.html', appointments=appointments)


@app.route('/activity_log')
def activity_log():
    cur = conn.cursor()
    cur.execute("SELECT * FROM activity_log")
    activity_log = cur.fetchall()
    return render_template('activity_log.html', activity_log=activity_log)


def log_activity(activity):
    cur = conn.cursor()
    cur.execute("INSERT INTO activity_log (activity) VALUES (%s)", (activity,))
    conn.commit()


# Example usage of log_activity function
@app.route('/some_activity')
def some_activity():
    # Perform the activity
    activity = 'Performed some activity'

    # Log the activity
    log_activity(activity)

    # Redirect or render a template
    return redirect(url_for('activity_log'))



if __name__ == '__main__':
    app.run(debug=True)
