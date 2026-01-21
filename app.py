from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import database  # Import our DB setup

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_this'  # Use a random string in production
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize DB on startup
database.init_db()

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('erp.db')
    user = conn.execute('SELECT id, username, role FROM Users WHERE id=?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect root to login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('erp.db')
        user = conn.execute('SELECT * FROM Users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):  # user[2] is password_hash
            user_obj = User(user[0], user[1], user[3])  # user[3] is role
            login_user(user_obj)
            if user[3] == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('teacher_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('login'))
    user_id = current_user.id
    conn = sqlite3.connect('erp.db')
    notices = conn.execute('SELECT title, content, date_posted FROM Notices ORDER BY date_posted DESC').fetchall()
    attendance = conn.execute('SELECT date, status FROM Attendance WHERE student_id=? ORDER BY date DESC', (user_id,)).fetchall()
    user_info = conn.execute('SELECT name, roll_no FROM Users WHERE id=?', (user_id,)).fetchone()
    conn.close()
    return render_template('student_dashboard.html', notices=notices, attendance=attendance, user_info=user_info)

@app.route('/teacher/dashboard', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('login'))
    conn = sqlite3.connect('erp.db')
    notices = conn.execute('SELECT id, title, content, date_posted FROM Notices ORDER BY date_posted DESC').fetchall()
    students = conn.execute('SELECT id, name, roll_no FROM Users WHERE role="student"').fetchall()
    attendance = conn.execute('SELECT a.id, u.name, a.date, a.status FROM Attendance a JOIN Users u ON a.student_id = u.id ORDER BY a.date DESC').fetchall()
    conn.close()
    
    if request.method == 'POST':
        if 'add_notice' in request.form:
            title = request.form['title']
            content = request.form['content']
            conn = sqlite3.connect('erp.db')
            conn.execute('INSERT INTO Notices (title, content, posted_by) VALUES (?, ?, ?)', (title, content, current_user.id))
            conn.commit()
            conn.close()
            flash('Notice added!')
            return redirect(url_for('teacher_dashboard'))
        elif 'mark_attendance' in request.form:
            student_id = request.form['student_id']
            date = request.form['date']
            status = request.form['status']
            conn = sqlite3.connect('erp.db')
            conn.execute('INSERT INTO Attendance (student_id, date, status, marked_by) VALUES (?, ?, ?, ?)', (student_id, date, status, current_user.id))
            conn.commit()
            conn.close()
            flash('Attendance marked!')
            return redirect(url_for('teacher_dashboard'))
    
    return render_template('teacher_dashboard.html', notices=notices, students=students, attendance=attendance)

if __name__ == '__main__':
    app.run(debug=True)