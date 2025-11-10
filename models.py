import bcrypt
from datetime import datetime
import re

class Course:
    def __init__(self, course_code, name, credits, lecture_hours, lab_hours, max_capacity, schedule_info, classroom, day_time):
        self.course_code = course_code
        self.name = name
        self.credits = credits
        self.lecture_hours = lecture_hours
        self.lab_hours = lab_hours
        self.max_capacity = max_capacity
        self.schedule_info = schedule_info
        self.classroom = classroom
        self.day_time = day_time
    
    def get_current_enrollment(self, db, semester):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM registrations 
            WHERE course_code = ? AND semester = ? AND status = 'registered'
        ''', (self.course_code, semester))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def is_full(self, db, semester):
        return self.get_current_enrollment(db, semester) >= self.max_capacity
    
    def check_prerequisites(self, db, student_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # الحصول على المتطلبات السابقة
        cursor.execute('''
            SELECT prerequisite_code FROM prerequisites 
            WHERE course_code = ?
        ''', (self.course_code,))
        prerequisites = [row[0] for row in cursor.fetchall()]
        
        # الحصول على المقررات التي اجتازها الطالب
        cursor.execute('''
            SELECT course_code FROM transcripts 
            WHERE student_id = ? AND grade >= 2.0
        ''', (student_id,))
        completed_courses = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # التحقق من استيفاء جميع المتطلبات
        return all(prereq in completed_courses for prereq in prerequisites)

class Student:
    def __init__(self, student_id, name, email, program, current_level, registration_year):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.program = program
        self.current_level = current_level
        self.registration_year = registration_year
    
    def get_completed_credits(self, db):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(c.credits) FROM transcripts t
            JOIN courses c ON t.course_code = c.course_code
            WHERE t.student_id = ? AND t.grade >= 2.0
        ''', (self.student_id,))
        result = cursor.fetchone()[0]
        conn.close()
        return result or 0
    
    def get_current_schedule(self, db, semester):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.* FROM registrations r
            JOIN courses c ON r.course_code = c.course_code
            WHERE r.student_id = ? AND r.semester = ? AND r.status = 'registered'
        ''', (self.student_id, semester))
        courses = cursor.fetchall()
        conn.close()
        return [Course(*course) for course in courses]
    
    def get_available_courses(self, db, semester):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # الحصول على المقررات المتاحة التي لم يسجل فيها الطالب ولم يكملها
        cursor.execute('''
            SELECT c.* FROM courses c
            WHERE c.course_code NOT IN (
                SELECT course_code FROM registrations 
                WHERE student_id = ? AND semester = ?
                UNION
                SELECT course_code FROM transcripts 
                WHERE student_id = ? AND grade >= 2.0
            )
        ''', (self.student_id, semester, self.student_id))
        
        available_courses = [Course(*row) for row in cursor.fetchall()]
        conn.close()
        return available_courses

class RegistrationSystem:
    def __init__(self, db):
        self.db = db
    
    def validate_registration(self, student, course_code, semester):
        errors = []
        warnings = []
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # الحصول على معلومات المقرر
        cursor.execute('SELECT * FROM courses WHERE course_code = ?', (course_code,))
        course_data = cursor.fetchone()
        
        if not course_data:
            errors.append(f"المقرر {course_code} غير موجود")
            return errors, warnings
        
        course = Course(*course_data)
        
        # التحقق من السعة
        if course.is_full(self.db, semester):
            errors.append(f"المقرر {course_code} ممتلئ")
        
        # التحقق من المتطلبات السابقة
        if not course.check_prerequisites(self.db, student.student_id):
            errors.append(f"لم تستكمل المتطلبات السابقة للمقرر {course_code}")
        
        # التحقق من التعارضات الزمنية
        current_courses = student.get_current_schedule(self.db, semester)
        for current_course in current_courses:
            if current_course.day_time == course.day_time:
                errors.append(f"تعارض زمني مع المقرر {current_course.course_code}")
        
        # التحقق من الحد الأقصى للساعات (18 ساعة)
        total_credits = sum(c.credits for c in current_courses) + course.credits
        if total_credits > 18:
            warnings.append(f"ستتجاوز الساعات المعتمدة الحد الأقصى (18 ساعة)")
        
        conn.close()
        return errors, warnings
    
    def register_course(self, student, course_code, semester):
        errors, warnings = self.validate_registration(student, course_code, semester)
        
        if errors:
            return False, errors + warnings
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO registrations (student_id, course_code, semester, status)
                VALUES (?, ?, ?, 'registered')
            ''', (student.student_id, course_code, semester))
            
            conn.commit()
            success = True
            message = ["تم التسجيل في المقرر بنجاح"] + warnings
        except Exception as e:
            conn.rollback()
            success = False
            message = [f"خطأ في قاعدة البيانات: {str(e)}"]
        finally:
            conn.close()
        
        return success, message
    
    def drop_course(self, student, course_code, semester):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM registrations 
                WHERE student_id = ? AND course_code = ? AND semester = ?
            ''', (student.student_id, course_code, semester))
            
            conn.commit()
            success = True
            message = "تم حذف المقرر بنجاح"
        except Exception as e:
            conn.rollback()
            success = False
            message = f"خطأ في قاعدة البيانات: {str(e)}"
        finally:
            conn.close()
        
        return success, message

class UserManager:
    def __init__(self, db):
        self.db = db
    
    def authenticate(self, user_id, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user[2]):
                    return {
                        'user_id': user[0],
                        'email': user[1],
                        'role': user[3],
                        'name': user[4]
