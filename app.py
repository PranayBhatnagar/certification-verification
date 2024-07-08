import os
import sqlite3
import uuid
from flask import Flask, render_template, request, url_for, redirect, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/certificates'
app.secret_key = 'supersecretkey'  # Needed for session management

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def init_db():
    conn = sqlite3.connect('certificates.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY,
            intern_name TEXT NOT NULL,
            job_role TEXT NOT NULL,
            certid TEXT UNIQUE NOT NULL,
            issue_date TEXT NOT NULL,
            certificate_image TEXT,
            other_details TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        # Process form data here (e.g., send email, save to database)
        flash('Thank you for contacting us! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'PROTECTED':
            session['logged_in'] = True
            return redirect(url_for('add_certificate'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))




@app.route('/add_certificate', methods=['GET', 'POST'])
def add_certificate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        intern_name = request.form['intern_name']
        job_role = request.form['job_role']
        issue_date = request.form['issue_date']
        certid = str(uuid.uuid4())
        
        certificate_image = request.files['certificate_image']
        if certificate_image:
            filename = secure_filename(certificate_image.filename)
            certificate_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            certificate_image.save(certificate_image_path)
            certificate_image_path = f'certificates/{filename}'
        else:
            certificate_image_path = None
        
        other_details = request.form['other_details']
        
        conn = sqlite3.connect('certificates.db')
        c = conn.cursor()
        c.execute('INSERT INTO certificates (intern_name, job_role, certid, issue_date, certificate_image, other_details) VALUES (?, ?, ?, ?, ?, ?)',
                  (intern_name, job_role, certid, issue_date, certificate_image_path, other_details))
        conn.commit()
        conn.close()
        
        verification_link = url_for('verify_certificate', certid=certid, _external=True)
        
        return f'Certificate added! Verification link: <a href="{verification_link}">{verification_link}</a>'
    return render_template('add_certificate.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        certid = request.form['certid']
        return redirect(url_for('verify_certificate', certid=certid))
    return render_template('verify.html')

@app.route('/verify/<string:certid>', methods=['GET'])
def verify_certificate(certid):
    conn = sqlite3.connect('certificates.db')
    c = conn.cursor()
    c.execute('SELECT * FROM certificates WHERE certid = ?', (certid,))
    certificate = c.fetchone()
    conn.close()
    
    if certificate:
        return render_template('verify.html', certificate=certificate)
    else:
        return "Certificate not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
