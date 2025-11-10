class Course:
    def __init__(self, course_code, name, credits, lecture_hours, lab_hours, max_capacity, schedule_info, classroom):
        self.course_code = course_code
        self.name = name
        self.credits = credits
        self.lecture_hours = lecture_hours
        self.lab_hours = lab_hours
        self.max_capacity = max_capacity
        self.schedule_info = schedule_info
        self.classroom = classroom

class Student:
    def __init__(self, student_id, name, email, program, current_level):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.program = program
        self.current_level = current_level

class UserManager:
    def __init__(self, db):
        self.db = db
    
    def authenticate(self, user_id, password):
        import bcrypt
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode(), user[2]):
            return {
                'user_id': user[0],
                'email': user[1],
                'role': user[3],
                'name': user[4]
            }
        return None
