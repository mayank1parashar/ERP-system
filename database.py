import sqlite3

def init_db():
    conn = sqlite3.connect('erp.db')  # Creates a file-based DB
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            roll_no TEXT,
            designation TEXT
        )
    ''')
    
    # Notices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            posted_by INTEGER NOT NULL,
            date_posted TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (posted_by) REFERENCES Users(id)
        )
    ''')
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            marked_by INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES Users(id),
            FOREIGN KEY (marked_by) REFERENCES Users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized!")

def add_sample_data():
    conn = sqlite3.connect('erp.db')
    cursor = conn.cursor()
    
    # Hash a sample password (use bcrypt in real code)
    from werkzeug.security import generate_password_hash
    hashed_pw = generate_password_hash('password123')
    
    # Sample users
    cursor.execute("INSERT OR IGNORE INTO Users (username, password_hash, role, name, roll_no, designation) VALUES (?, ?, ?, ?, ?, ?)",
                   ('student1', hashed_pw, 'student', 'John Doe', '101', None))
    cursor.execute("INSERT OR IGNORE INTO Users (username, password_hash, role, name, roll_no, designation) VALUES (?, ?, ?, ?, ?, ?)",
                   ('teacher1', hashed_pw, 'teacher', 'Jane Smith', None, 'Professor'))
    
    # Sample notice
    cursor.execute("INSERT OR IGNORE INTO Notices (title, content, posted_by) VALUES (?, ?, ?)",
                   ('Welcome Notice', 'Institute opens at 9 AM.', 2))  # posted_by = teacher ID
    
    # Sample attendance
    cursor.execute("INSERT OR IGNORE INTO Attendance (student_id, date, status, marked_by) VALUES (?, ?, ?, ?)",
                   (1, '2023-10-01', 'present', 2))
    
    conn.commit()
    conn.close()
    print("Sample data added!")

if __name__ == '__main__':
    init_db()
    add_sample_data()