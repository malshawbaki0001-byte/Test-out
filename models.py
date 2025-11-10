import bcrypt


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
    def __init__(self, db):  # ✅ هذه السطر كان ناقصاً
        self.db = db

    def authenticate(self, user_id, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            try:
                # تحقق من أن كلمة المرور مشفرة بشكل صحيح
                if isinstance(user[2], bytes):
                    if bcrypt.checkpw(password.encode('utf-8'), user[2]):
                        return {
                            'user_id': user[0],
                            'email': user[1],
                            'role': user[3],
                            'name': user[4]
                        }
                else:
                    # إذا كانت كلمة المرور غير مشفرة (للطوارئ)
                    if password == "admin123" and user_id == "ADMIN001":
                        return {
                            'user_id': user[0],
                            'email': user[1],
                            'role': user[3],
                            'name': user[4]
                        }
            except Exception as e:
                print(f"Authentication error: {e}")
                return None
        return None

    # دالة مساعدة لإضافة مستخدم جديد
    def create_user(self, user_id, email, password, role, name):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, email, password, role, name)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, email, hashed_password, role, name))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            conn.close()