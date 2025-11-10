import sqlite3
import bcrypt
from datetime import datetime

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
                classroom TEXT NOT NULL,
                day_time TEXT NOT NULL
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
        
        # جدول التسجيلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                course_code TEXT,
                semester TEXT NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'registered',
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_code) REFERENCES courses(course_code)
            )
        ''')
        
        # جدول السجلات الدراسية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcripts (
                student_id TEXT,
                course_code TEXT,
                grade REAL NOT NULL,
                semester TEXT NOT NULL,
                PRIMARY KEY (student_id, course_code),
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_code) REFERENCES courses(course_code)
            )
        ''')
        
        conn.commit()
        self.add_sample_data()
        conn.close()
    
    def add_sample_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # إضافة مسؤول
            admin_password = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, email, password, role, name)
                VALUES (?, ?, ?, ?, ?)
            ''', ("ADMIN001", "admin@ece.edu", admin_password, "admin", "System Administrator"))
            
            # إضافة طلاب
            students = [
                ("STU001", "student1@ece.edu", "Computer", 3, "Ahmed Ali"),
                ("STU002", "student2@ece.edu", "Communications", 2, "Fatima Mohammed"),
                ("STU003", "student3@ece.edu", "Power", 4, "Khalid Hassan")
            ]
            
            for student_id, email, program, level, name in students:
                student_password = bcrypt.hashpw(b"student123", bcrypt.gensalt())
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, email, password, role, name)
                    VALUES (?, ?, ?, 'student', ?)
                ''', (student_id, email, student_password, name))
                
                cursor.execute('''
                    INSERT OR REPLACE INTO students (student_id, program, current_level)
                    VALUES (?, ?, ?)
                ''', (student_id, program, level))
            
            # إضافة مقررات
            courses = [
                ("COE100", "Programming Fundamentals", 3, 3, 0, 50, "Mon-Wed 10:00-11:30", "Room 101", "Monday 10:00-11:30"),
                ("COE200", "Data Structures", 3, 3, 0, 40, "Tue-Thu 09:00-10:30", "Room 102", "Tuesday 09:00-10:30"),
                ("COE210", "Digital Logic Design", 4, 3, 2, 35, "Mon-Wed 13:00-14:30", "Lab A", "Monday 13:00-14:30"),
                ("COE300", "Algorithms", 3, 3, 0, 45, "Tue-Thu 11:00-12:30", "Room 103", "Tuesday 11:00-12:30"),
                ("COE310", "Computer Architecture", 4, 3, 2, 30, "Mon-Wed 15:00-16:30", "Lab B", "Monday 15:00-16:30"),
                ("COE320", "Database Systems", 3, 3, 0, 40, "Wed-Fri 10:00-11:30", "Room 104", "Wednesday 10:00-11:30"),
                ("COE400", "Software Engineering", 3, 3, 0, 35, "Thu-Sat 14:00-15:30", "Room 105", "Thursday 14:00-15:30")
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO courses 
                (course_code, name, credits, lecture_hours, lab_hours, max_capacity, schedule_info, classroom, day_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', courses)
            
            # إضافة متطلبات سابقة
            prerequisites = [
                ("COE200", "COE100"),
                ("COE300", "COE200"),
                ("COE310", "COE210"),
                ("COE400", "COE300")
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO prerequisites (course_code, prerequisite_code)
                VALUES (?, ?)
            ''', prerequisites)
            
            # إضافة سجلات دراسية للطلاب
            transcripts = [
                ("STU001", "COE100", 3.5, "2023-Fall"),
                ("STU001", "COE200", 3.0, "2024-Spring"),
                ("STU002", "COE100", 2.8, "2023-Fall"),
                ("STU003", "COE100", 3.2, "2023-Fall"),
                ("STU003", "COE200", 3.4, "2024-Spring"),
                ("STU003", "COE210", 3.1, "2024-Spring")
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO transcripts (student_id, course_code, grade, semester)
                VALUES (?, ?, ?, ?)
            ''', transcripts)
            
            conn.commit()
            print("✓ تم إضافة البيانات الأولية بنجاح")
        except Exception as e:
            print(f"✗ خطأ في إضافة البيانات: {e}")
        finally:
            conn.close()
