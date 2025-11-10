import sqlite3
import bcrypt

class Database:
    def __init__(self, db_name="course_registration.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
                name TEXT NOT NULL
            )
        ''')
        
        # جدول الطلاب
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                program TEXT NOT NULL CHECK(program IN ('Computer', 'Communications', 'Power', 'Biomedical')),
                current_level INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول المقررات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                credits INTEGER NOT NULL CHECK(credits > 0),
                lecture_hours INTEGER NOT NULL,
                lab_hours INTEGER NOT NULL,
                max_capacity INTEGER NOT NULL,
                schedule_info TEXT NOT NULL,
                classroom TEXT NOT NULL
            )
        ''')
        
        # جدول المتطلبات السابقة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prerequisites (
                course_code TEXT,
                prerequisite_code TEXT,
                PRIMARY KEY (course_code, prerequisite_code),
                FOREIGN KEY (course_code) REFERENCES courses(course_code),
                FOREIGN KEY (prerequisite_code) REFERENCES courses(course_code)
            )
        ''')
        
        conn.commit()
        
        # إضافة بيانات أولية
        self.add_sample_data(conn)
        conn.close()
    
    def add_sample_data(self, conn):
        cursor = conn.cursor()
        
        # إضافة مستخدم مسؤول
        try:
            admin_password = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, email, password, role, name)
                VALUES (?, ?, ?, ?, ?)
            ''', ("ADMIN001", "admin@ece.edu", admin_password, "admin", "System Administrator"))
        except:
            pass
        
        # إضافة مقررات نموذجية
        sample_courses = [
            ("COE100", "Programming Fundamentals", 3, 3, 0, 50, "Mon-Wed 10:00-11:30", "Room 101"),
            ("COE200", "Data Structures", 3, 3, 0, 40, "Tue-Thu 09:00-10:30", "Room 102"),
            ("COE210", "Digital Logic Design", 4, 3, 2, 35, "Mon-Wed 13:00-14:30", "Lab A"),
            ("COE300", "Algorithms", 3, 3, 0, 45, "Tue-Thu 11:00-12:30", "Room 103"),
            ("COE310", "Computer Architecture", 4, 3, 2, 30, "Mon-Wed 15:00-16:30", "Lab B"),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO courses 
            (course_code, name, credits, lecture_hours, lab_hours, max_capacity, schedule_info, classroom)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_courses)
        
        # إضافة متطلبات سابقة
        prerequisites = [
            ("COE200", "COE100"),
            ("COE300", "COE200"),
            ("COE310", "COE210"),
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO prerequisites (course_code, prerequisite_code)
            VALUES (?, ?)
        ''', prerequisites)
        
        conn.commit()
