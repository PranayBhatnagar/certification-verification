from flask import Flask, render_template, request
import sqlite3
import uuid
import os

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('DROP TABLE IF EXISTS certificates')  # Drop existing table if it exists
    conn.execute('''
        CREATE TABLE certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intern_name TEXT NOT NULL,
            job_role TEXT NOT NULL,
            certificate_id TEXT NOT NULL UNIQUE,
            issue_date TEXT NOT NULL,
            certificate_image TEXT,
            other_details TEXT
        )
    ''')
    print("Database initialized successfully")
    conn.close()

init_db()

# Route to add certificates
@app.route('/add_certificate', methods=['GET', 'POST'])
def add_certificate():
    if request.method == 'POST':
        intern_name = request.form['intern_name']
        job_role = request.form['job_role']
        issue_date = request.form['issue_date']
        other_details = request.form['other_details']

        # Handle certificate image upload
        certificate_image = None
        if 'certificate_image' in request.files:
            certificate_image = request.files['certificate_image']
            if certificate_image.filename != '':
                filename = str(uuid.uuid4()) + os.path.splitext(certificate_image.filename)[1]
                certificate_image.save(os.path.join('static/uploads', filename))
                certificate_image_path = f'static/uploads/{filename}'
            else:
                certificate_image_path = None

        # Generate a unique certificate ID (using UUID)
        certificate_id = str(uuid.uuid4())

        # Insert certificate into database
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('INSERT INTO certificates (intern_name, job_role, certificate_id, issue_date, certificate_image, other_details) VALUES (?, ?, ?, ?, ?, ?)',
                    (intern_name, job_role, certificate_id, issue_date, certificate_image_path, other_details))
        conn.commit()
        conn.close()

        return f'Certificate added successfully. Certificate ID: {certificate_id}'

    return '''
        <form method="post" enctype="multipart/form-data">
            <p>Intern Name: <input type="text" name="intern_name" required></p>
            <p>Job Role: <input type="text" name="job_role" required></p>
            <p>Issue Date: <input type="text" name="issue_date" required></p>
            <p>Other Details: <input type="text" name="other_details"></p>
            <p>Upload Certificate Image: <input type="file" name="certificate_image"></p>
            <p><input type="submit" value="Add Certificate"></p>
        </form>
    '''

# Route to verify certificates
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        cert_id = request.form['certid']
        certificate = get_certificate(cert_id)
        if certificate:
            return render_template('verify.html', certificate=certificate)
        else:
            return "Certificate not found."
    return render_template('verify.html')

# Function to fetch certificate details from database
def get_certificate(cert_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM certificates WHERE certificate_id = ?', (cert_id,))
    certificate = cur.fetchone()
    conn.close()
    return certificate

if __name__ == '__main__':
    app.run(debug=True)
