"""
================================================================================
Database Layer - طبقة قاعدة البيانات (الإصدار المبسط للمبتدئين)
================================================================================

هذا الملف يحتوي على جميع العمليات المتعلقة بقاعدة البيانات.
تم تصميمه بشكل بسيط ليكون سهل الفهم والشرح للمبرمجين المبتدئين.

الفكرة الأساسية:
- كل جدول له كلاس منفصل
- كل كلاس يحتوي على الوظائف الأساسية (إضافة، حذف، تحديث، جلب)
- الكود واضح ومُعلق بشكل جيد
- فصل المسؤوليات بشكل واضح
"""

import sqlite3
from typing import List, Tuple, Optional, Dict
import os

class DatabaseLayer:
    """
    الكلاس الرئيسي لطبقة قاعدة البيانات
    يحتوي على جميع العمليات الأساسية للتعامل مع قاعدة البيانات
    """

    # إعدادات قاعدة البيانات
    DATABASE_NAME = "plans.db"
    ALLOWED_PROGRAMS = ["Computer", "Comm", "Power", "Biomedical"]

    @staticmethod
    def GetConnection():
        """
        إنشاء اتصال جديد بقاعدة البيانات

        Returns:
            sqlite3.Connection: كائن الاتصال بقاعدة البيانات
        """
        connection = sqlite3.connect(DatabaseLayer.DATABASE_NAME)
        # تفعيل دعم المفاتيح الخارجية
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    @staticmethod
    def InitializeDatabase():
        """
        إنشاء الجداول الأساسية في قاعدة البيانات
        يتم استدعاء هذا الدالة مرة واحدة عند بدء تشغيل البرنامج
        """
        connection = DatabaseLayer.GetConnection()
        cursor = connection.cursor()

        # ============================================
        # جدول المقررات (Courses)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_code TEXT PRIMARY KEY,    -- رمز المقرر (مثل: EE202)
                name TEXT NOT NULL,              -- اسم المقرر
                credits INTEGER NOT NULL,        -- عدد الساعات المعتمدة
                has_lab INTEGER DEFAULT 0,       -- هل المادة تحتوي على مختبر (0=لا, 1=نعم)
                level INTEGER DEFAULT 1          -- المستوى الدراسي
            )
        ''')

        # ============================================
        # جدول المتطلبات السابقة (Prerequisites)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prerequisites (
                course_code TEXT NOT NULL,       -- رمز المقرر الأساسي
                prereq_code TEXT NOT NULL,        -- رمز المقرر المطلوب كشرط سابق
                PRIMARY KEY (course_code, prereq_code),
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE,
                FOREIGN KEY (prereq_code) REFERENCES courses(course_code) ON DELETE RESTRICT
            )
        ''')

        # ============================================
        # جدول الشعب (Sections)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                section_id TEXT PRIMARY KEY,      -- معرف الشعبة (مثل: EE202-01)
                course_code TEXT NOT NULL,        -- رمز المقرر
                instructor TEXT NOT NULL,         -- اسم المدرس
                -- بيانات المحاضرة
                lecture_start_time INTEGER,       -- وقت بداية المحاضرة
                lecture_end_time INTEGER,         -- وقت نهاية المحاضرة
                lecture_days TEXT DEFAULT '',     -- أيام المحاضرة
                lecture_hall TEXT,                -- قاعة المحاضرة
                -- بيانات المختبر
                lab_start_time INTEGER,           -- وقت بداية المختبر
                lab_end_time INTEGER,             -- وقت نهاية المختبر
                lab_days TEXT DEFAULT '',         -- أيام المختبر
                lab_hall TEXT,                    -- قاعة المختبر
                -- بيانات عامة
                max_capacity INTEGER NOT NULL,    -- السعة القصوى
                current_enrollment INTEGER DEFAULT 0, -- عدد المسجلين الحالي
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE
            )
        ''')

        # ============================================
        # جدول الطلاب (Students)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,      -- رقم الطالب الجامعي
                name TEXT NOT NULL,               -- اسم الطالب
                email TEXT NOT NULL,              -- البريد الإلكتروني
                program TEXT NOT NULL,            -- البرنامج الدراسي
                level INTEGER NOT NULL            -- المستوى الدراسي الحالي
            )
        ''')

        # ============================================
        # جدول السجل الأكاديمي (Transcripts)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcripts (
                student_id TEXT NOT NULL,         -- رقم الطالب
                course_code TEXT NOT NULL,        -- رمز المقرر المجتاز
                PRIMARY KEY (student_id, course_code),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE RESTRICT
            )
        ''')

        # ============================================
        # جدول التسجيلات (Registrations)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                student_id TEXT NOT NULL,         -- رقم الطالب
                section_id TEXT NOT NULL,         -- معرف الشعبة
                registration_time TEXT NOT NULL,  -- وقت التسجيل
                PRIMARY KEY (student_id, section_id),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE
            )
        ''')

        # ============================================
        # جدول المستخدمين (Users)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- معرف فريد للمستخدم
                student_id TEXT UNIQUE,           -- رقم الطالب (إذا كان طالباً)
                email TEXT UNIQUE NOT NULL,       -- البريد الإلكتروني
                password_hash TEXT NOT NULL,      -- كلمة المرور المشفرة
                role TEXT NOT NULL,               -- الدور (student أو admin)
                display_name TEXT,                -- الاسم المعروض
                mobile TEXT                       -- رقم الجوال
            )
        ''')

        # ============================================
        # جدول الاساتذة (Professors)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id TEXT PRIMARY KEY,       -- معرف الدكتور
                name TEXT NOT NULL,               -- اسم الدكتور
                email TEXT UNIQUE NOT NULL,       -- البريد الإلكتروني
                preferred_courses TEXT DEFAULT '', -- المقررات المفضلة
                time_availability TEXT DEFAULT ''  -- أوقات التوفر
            )
        ''')

        # ============================================
        # جدول تعيينات الاساتذة (Professor Assignments)
        # ============================================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_assignments (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- معرف التعيين
                doctor_id TEXT NOT NULL,            -- معرف الدكتور
                course_code TEXT NOT NULL,          -- رمز المقرر
                section_id TEXT,                    -- معرف الشعبة (اختياري)
                FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE CASCADE,
                FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE SET NULL
            )
        ''')

        # حفظ التغييرات
        connection.commit()
        connection.close()

        print("✅ تم إنشاء قاعدة البيانات بنجاح!")

    # ============================================================================
    # كلاس إدارة المقررات
    # ============================================================================

    class CourseManager:
        """
        إدارة المقررات الدراسية
        يحتوي على جميع العمليات المتعلقة بالمقررات
        """

        @staticmethod
        def AddCourse(course_code: str, name: str, credits: int, has_lab: bool = False, level: int = 1) -> bool:
            """
            إضافة مقرر جديد

            Args:
                course_code: رمز المقرر
                name: اسم المقرر
                credits: عدد الساعات المعتمدة
                has_lab: هل المادة تحتوي على مختبر
                level: المستوى الدراسي

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT INTO courses (course_code, name, credits, has_lab, level)
                    VALUES (?, ?, ?, ?, ?)
                ''', (course_code, name, credits, int(has_lab), level))

                connection.commit()
                return True

            except sqlite3.IntegrityError:
                # المقرر موجود مسبقاً
                return False
            except Exception as e:
                print(f"خطأ في إضافة المقرر: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def InsertOrUpdateCourse(course_code: str, name: str, credits: int, has_lab: bool, level: int) -> bool:
            """
            إضافة أو تحديث مقرر

            Args:
                course_code: رمز المقرر
                name: اسم المقرر
                credits: عدد الساعات المعتمدة
                has_lab: هل المادة تحتوي على مختبر
                level: المستوى الدراسي

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO courses (course_code, name, credits, has_lab, level)
                    VALUES (?, ?, ?, ?, ?)
                ''', (course_code, name, credits, int(has_lab), level))

                connection.commit()
                return True
            except Exception as e:
                print(f"خطأ في حفظ المقرر: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def GetCourse(course_code: str) -> Optional[Dict]:
            
            # جلب بيانات مقرر محدد

            # Args:
            #     course_code: رمز المقرر

            # Returns:
            #     Dict أو None: بيانات المقرر إذا وُجد
            
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('''
                SELECT course_code, name, credits, has_lab, level
                FROM courses
                WHERE course_code = ?
            ''', (course_code,))

            row = cursor.fetchone()
            connection.close()

            if row:
                return {
                    "course_code": row[0],
                    "name": row[1],
                    "credits": row[2],
                    "has_lab": bool(row[3]),
                    "level": row[4]
                }
            return None

        @staticmethod
        def GetAllCourses() -> List[Dict]:
            """
            جلب جميع المقررات

            Returns:
                List[Dict]: قائمة بجميع المقررات
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('SELECT course_code, name, credits, has_lab, level FROM courses ORDER BY course_code')

            courses = []
            for row in cursor.fetchall():
                courses.append({
                    "course_code": row[0],
                    "name": row[1],
                    "credits": row[2],
                    "has_lab": bool(row[3]),
                    "level": row[4]
                })

            connection.close()
            return courses

        @staticmethod
        def DeleteCourse(course_code: str) -> bool:
            """
            حذف مقرر

            Args:
                course_code: رمز المقرر المراد حذفه

            Returns:
                bool: True إذا نجح الحذف
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('DELETE FROM courses WHERE course_code = ?', (course_code,))

                connection.commit()
                return cursor.rowcount > 0  # نجح إذا تم حذف صف واحد على الأقل

            except Exception as e:
                print(f"خطأ في حذف المقرر: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def FetchAllCoursesWithSections() -> Dict[str, Dict]:
            """
            جلب جميع المقررات مع شعبها

            Returns:
                Dict: قاموس يربط كود المقرر ببياناته والشعب التابعة له
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            # جلب المقررات
            cursor.execute('''
                SELECT course_code, name, credits, has_lab, level
                FROM courses
                ORDER BY course_code
            ''')

            courses_data = {}
            for row in cursor.fetchall():
                course_code = row[0]
                courses_data[course_code] = {
                    'course_code': course_code,
                    'name': row[1],
                    'credit_hours': row[2],
                    'has_lab': bool(row[3]),
                    'level': row[4],
                    'prerequisites': [],
                    'sections': []
                }

            # جلب المتطلبات السابقة
            cursor.execute('SELECT course_code, prereq_code FROM prerequisites')
            for row in cursor.fetchall():
                course_code, prereq_code = row
                if course_code in courses_data:
                    courses_data[course_code]['prerequisites'].append(prereq_code)

            # جلب الشعب
            cursor.execute('''
                SELECT section_id, course_code, instructor,
                       lecture_start_time, lecture_end_time, lecture_days, lecture_hall,
                       lab_start_time, lab_end_time, lab_days, lab_hall,
                       max_capacity, current_enrollment
                FROM sections
                ORDER BY section_id
            ''')

            for row in cursor.fetchall():
                section_id, course_code = row[0], row[1]
                if course_code in courses_data:
                    section_data = {
                        'id': section_id,
                        'instructor': row[2],
                        'lecture_start': row[3],
                        'lecture_end': row[4],
                        'lecture_days': row[5] or '',
                        'lecture_hall': row[6] or '',
                        'lab_start': row[7],
                        'lab_end': row[8],
                        'lab_days': row[9] or '',
                        'lab_hall': row[10] or '',
                        'max_capacity': row[11],
                        'current_enrollment': row[12] or 0,
                        'days': row[5] or '',  # للتوافق مع الكود القديم
                        'start': row[3],       # للتوافق مع الكود القديم
                        'end': row[4],         # للتوافق مع الكود القديم
                        'hall': row[6] or ''   # للتوافق مع الكود القديم
                    }
                    courses_data[course_code]['sections'].append(section_data)

            connection.close()
            return courses_data

    # ============================================================================
    # كلاس إدارة الشعب
    # ============================================================================

    class SectionManager:
        """
        إدارة الشعب الدراسية
        يحتوي على جميع العمليات المتعلقة بالشعب
        """

        @staticmethod
        def AddSection(section_id: str, course_code: str, instructor: str,
                      lecture_start: int = None, lecture_end: int = None, lecture_days: str = None, lecture_hall: str = None,
                      lab_start: int = None, lab_end: int = None, lab_days: str = None, lab_hall: str = None,
                      max_capacity: int = 0, current_enrollment: int = 0) -> bool:
            """
            إضافة شعبة جديدة

            Args:
                section_id: معرف الشعبة
                course_code: رمز المقرر
                instructor: اسم المدرس
                lecture_start, lecture_end, lecture_days, lecture_hall: بيانات المحاضرة
                lab_start, lab_end, lab_days, lab_hall: بيانات المختبر
                max_capacity: السعة القصوى
                current_enrollment: عدد المسجلين الحالي

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT INTO sections (section_id, course_code, instructor,
                                       lecture_start_time, lecture_end_time, lecture_days, lecture_hall,
                                       lab_start_time, lab_end_time, lab_days, lab_hall,
                                       max_capacity, current_enrollment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (section_id, course_code, instructor,
                      lecture_start, lecture_end, lecture_days, lecture_hall,
                      lab_start, lab_end, lab_days, lab_hall,
                      max_capacity, current_enrollment))

                connection.commit()
                return True

            except sqlite3.IntegrityError:
                # الشعبة موجودة مسبقاً
                return False
            except Exception as e:
                print(f"خطأ في إضافة الشعبة: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def InsertOrUpdateSection(section_id: str, course_code: str, instructor: str,
                                 lecture_start: int = None, lecture_end: int = None, lecture_days: str = None, lecture_hall: str = None,
                                 lab_start: int = None, lab_end: int = None, lab_days: str = None, lab_hall: str = None,
                                 max_capacity: int = 0, current_enrollment: int = 0) -> bool:
            """
            إضافة أو تحديث شعبة

            Args:
                section_id: معرف الشعبة
                course_code: رمز المقرر
                instructor: اسم المدرس
                lecture_start, lecture_end, lecture_days, lecture_hall: بيانات المحاضرة
                lab_start, lab_end, lab_days, lab_hall: بيانات المختبر
                max_capacity: السعة القصوى
                current_enrollment: عدد المسجلين الحالي

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO sections (section_id, course_code, instructor,
                                                   lecture_start_time, lecture_end_time, lecture_days, lecture_hall,
                                                   lab_start_time, lab_end_time, lab_days, lab_hall,
                                                   max_capacity, current_enrollment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (section_id, course_code, instructor,
                      lecture_start, lecture_end, lecture_days, lecture_hall,
                      lab_start, lab_end, lab_days, lab_hall,
                      max_capacity, current_enrollment))

                connection.commit()
                return True
            except Exception as e:
                print(f"خطأ في حفظ الشعبة: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def GetSectionsForCourse(course_code: str) -> List[Dict]:
            """
            جلب جميع الشعب لمقرر محدد

            Args:
                course_code: رمز المقرر

            Returns:
                List[Dict]: قائمة بالشعب
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('''
                SELECT section_id, course_code, instructor,
                       lecture_start_time, lecture_end_time, lecture_days, lecture_hall,
                       lab_start_time, lab_end_time, lab_days, lab_hall,
                       max_capacity, current_enrollment
                FROM sections
                WHERE course_code = ?
                ORDER BY section_id
            ''', (course_code,))

            sections = []
            for row in cursor.fetchall():
                sections.append({
                    "section_id": row[0],
                    "course_code": row[1],
                    "instructor": row[2],
                    "lecture_start": row[3],
                    "lecture_end": row[4],
                    "lecture_days": row[5] or '',
                    "lecture_hall": row[6] or '',
                    "lab_start": row[7],
                    "lab_end": row[8],
                    "lab_days": row[9] or '',
                    "lab_hall": row[10] or '',
                    "max_capacity": row[11],
                    "current_enrollment": row[12] or 0,
                    # للتوافق مع الكود القديم
                    "start_time": row[3],  # lecture_start
                    "end_time": row[4],    # lecture_end
                    "hall": row[6] or '',  # lecture_hall
                    "days": row[5] or ''   # lecture_days
                })

            connection.close()
            return sections

        @staticmethod
        def GetSection(section_id: str) -> Optional[Dict]:
            """
            جلب بيانات شعبة محددة

            Args:
                section_id: معرف الشعبة

            Returns:
                Dict أو None: بيانات الشعبة إذا وُجدت
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('''
                SELECT section_id, course_code, instructor,
                       lecture_start_time, lecture_end_time, lecture_days, lecture_hall,
                       lab_start_time, lab_end_time, lab_days, lab_hall,
                       max_capacity, current_enrollment
                FROM sections
                WHERE section_id = ?
            ''', (section_id,))

            row = cursor.fetchone()
            connection.close()

            if row:
                return {
                    "section_id": row[0],
                    "course_code": row[1],
                    "instructor": row[2],
                    "lecture_start": row[3],
                    "lecture_end": row[4],
                    "lecture_days": row[5] or '',
                    "lecture_hall": row[6] or '',
                    "lab_start": row[7],
                    "lab_end": row[8],
                    "lab_days": row[9] or '',
                    "lab_hall": row[10] or '',
                    "max_capacity": row[11],
                    "current_enrollment": row[12] or 0,
                    # للتوافق مع الكود القديم
                    "start_time": row[3],  # lecture_start
                    "end_time": row[4],    # lecture_end
                    "hall": row[6] or '',  # lecture_hall
                    "days": row[5] or ''   # lecture_days
                }
            return None

        @staticmethod
        def EnrollStudent(section_id: str) -> bool:
            """
            تسجيل طالب في شعبة (زيادة عدد المسجلين)

            Args:
                section_id: معرف الشعبة

            Returns:
                bool: True إذا نجح التسجيل
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                # التحقق من أن الشعبة غير ممتلئة
                cursor.execute('SELECT current_enrollment, max_capacity FROM sections WHERE section_id = ?', (section_id,))
                row = cursor.fetchone()

                if not row:
                    return False  # الشعبة غير موجودة

                current, max_capacity = row
                if current >= max_capacity:
                    return False  # الشعبة ممتلئة

                # زيادة عدد المسجلين
                cursor.execute('UPDATE sections SET current_enrollment = current_enrollment + 1 WHERE section_id = ?', (section_id,))
                connection.commit()
                return True

            except Exception as e:
                print(f"خطأ في تسجيل الطالب: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def UnenrollStudent(section_id: str) -> bool:
            """
            إلغاء تسجيل طالب من شعبة (نقصان عدد المسجلين)

            Args:
                section_id: معرف الشعبة

            Returns:
                bool: True إذا نجح الإلغاء
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                # التحقق من وجود مسجلين
                cursor.execute('SELECT current_enrollment FROM sections WHERE section_id = ?', (section_id,))
                row = cursor.fetchone()

                if not row or row[0] <= 0:
                    return False  # لا يوجد مسجلين أو الشعبة غير موجودة

                # نقصان عدد المسجلين
                cursor.execute('UPDATE sections SET current_enrollment = current_enrollment - 1 WHERE section_id = ?', (section_id,))
                connection.commit()
                return True

            except Exception as e:
                print(f"خطأ في إلغاء تسجيل الطالب: {e}")
                return False
            finally:
                connection.close()

    # ============================================================================
    # كلاس إدارة الطلاب
    # ============================================================================

    class StudentManager:
        """
        إدارة الطلاب
        يحتوي على جميع العمليات المتعلقة بالطلاب
        """

        @staticmethod
        def AddStudent(student_id: str, name: str, email: str, program: str, level: int) -> bool:
            """
            إضافة طالب جديد

            Args:
                student_id: رقم الطالب الجامعي
                name: اسم الطالب
                email: البريد الإلكتروني
                program: البرنامج الدراسي
                level: المستوى الدراسي

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT INTO students (student_id, name, email, program, level)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, name, email, program, level))

                connection.commit()
                return True

            except sqlite3.IntegrityError:
                # الطالب موجود مسبقاً
                return False
            except Exception as e:
                print(f"خطأ في إضافة الطالب: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def GetStudent(student_id: str) -> Optional[Dict]:
            """
            جلب بيانات طالب محدد

            Args:
                student_id: رقم الطالب

            Returns:
                Dict أو None: بيانات الطالب إذا وُجد
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('''
                SELECT student_id, name, email, program, level
                FROM students
                WHERE student_id = ?
            ''', (student_id,))

            row = cursor.fetchone()
            connection.close()

            if row:
                return {
                    "student_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "program": row[3],
                    "level": row[4]
                }
            return None

        @staticmethod
        def GetAllStudents() -> List[Dict]:
            """
            جلب جميع الطلاب

            Returns:
                List[Dict]: قائمة بجميع الطلاب
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('SELECT student_id, name, email, program, level FROM students ORDER BY student_id')

            students = []
            for row in cursor.fetchall():
                students.append({
                    "student_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "program": row[3],
                    "level": row[4]
                })

            connection.close()
            return students

        @staticmethod
        def GetStudentTranscript(student_id: str) -> List[str]:
            """
            جلب السجل الأكاديمي للطالب (المقررات المجتازة)

            Args:
                student_id: رقم الطالب

            Returns:
                List[str]: قائمة برموز المقررات المجتازة
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('SELECT course_code FROM transcripts WHERE student_id = ?', (student_id,))

            transcript = [row[0] for row in cursor.fetchall()]
            connection.close()

            return transcript

        @staticmethod
        def AddCourseToTranscript(student_id: str, course_code: str) -> bool:
            """
            إضافة مقرر للسجل الأكاديمي للطالب

            Args:
                student_id: رقم الطالب
                course_code: رمز المقرر

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT OR IGNORE INTO transcripts (student_id, course_code)
                    VALUES (?, ?)
                ''', (student_id, course_code))

                connection.commit()
                return True

            except Exception as e:
                print(f"خطأ في إضافة المقرر للسجل: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def RegisterForSection(student_id: str, section_id: str, registration_time: str) -> bool:
            """
            تسجيل طالب في شعبة

            Args:
                student_id: رقم الطالب
                section_id: معرف الشعبة
                registration_time: وقت التسجيل

            Returns:
                bool: True إذا نجح التسجيل
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT INTO registrations (student_id, section_id, registration_time)
                    VALUES (?, ?, ?)
                ''', (student_id, section_id, registration_time))

                connection.commit()

                # زيادة عدد المسجلين في الشعبة
                DatabaseLayer.SectionManager.EnrollStudent(section_id)

                return True

            except sqlite3.IntegrityError:
                # التسجيل موجود مسبقاً
                return False
            except Exception as e:
                print(f"خطأ في التسجيل: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def GetStudentRegistrations(student_id: str) -> List[Dict]:
            """
            جلب التسجيلات الحالية للطالب

            Args:
                student_id: رقم الطالب

            Returns:
                List[Dict]: قائمة بالتسجيلات
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('''
                SELECT section_id, registration_time
                FROM registrations
                WHERE student_id = ?
                ORDER BY registration_time
            ''', (student_id,))

            registrations = []
            for row in cursor.fetchall():
                registrations.append({
                    "section_id": row[0],
                    "registration_time": row[1]
                })

            connection.close()
            return registrations

    # ============================================================================
    # كلاس إدارة المستخدمين
    # ============================================================================

    class UserManager:
        """
        إدارة المستخدمين والمصادقة
        يحتوي على جميع العمليات المتعلقة بالمستخدمين
        """

        @staticmethod
        def CreateUser(student_id: Optional[str], email: str, password_hash: str, role: str, display_name: str = "", mobile: str = "") -> bool:
            """
            إنشاء مستخدم جديد

            Args:
                student_id: رقم الطالب (اختياري)
                email: البريد الإلكتروني
                password_hash: كلمة المرور المشفرة
                role: الدور (student أو admin)
                display_name: الاسم المعروض
                mobile: رقم الجوال

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT INTO users (student_id, email, password_hash, role, display_name, mobile)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (student_id, email, password_hash, role, display_name, mobile))

                connection.commit()
                return True

            except sqlite3.IntegrityError:
                # المستخدم موجود مسبقاً
                return False
            except Exception as e:
                print(f"خطأ في إنشاء المستخدم: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def AuthenticateUser(identifier: str, password_hash: str) -> Optional[Dict]:
            """
            المصادقة على المستخدم

            Args:
                identifier: المعرف (رقم الطالب أو البريد الإلكتروني)
                password_hash: كلمة المرور المشفرة

            Returns:
                Dict أو None: بيانات المستخدم إذا نجحت المصادقة
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('''
                SELECT user_id, student_id, email, password_hash, role, display_name, mobile
                FROM users
                WHERE (student_id = ? OR email = ?) AND password_hash = ?
            ''', (identifier, identifier, password_hash))

            row = cursor.fetchone()
            connection.close()

            if row:
                return {
                    "user_id": row[0],
                    "student_id": row[1],
                    "email": row[2],
                    "password_hash": row[3],
                    "role": row[4],
                    "display_name": row[5],
                    "mobile": row[6]
                }
            return None

        @staticmethod
        def GetUserByEmail(email: str) -> Optional[Dict]:
            """
            البحث عن مستخدم بالبريد الإلكتروني

            Args:
                email: البريد الإلكتروني

            Returns:
                Dict أو None: بيانات المستخدم إذا وُجد
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('SELECT user_id, student_id, email, role, display_name, mobile FROM users WHERE email = ?', (email,))

            row = cursor.fetchone()
            connection.close()

            if row:
                return {
                    "user_id": row[0],
                    "student_id": row[1],
                    "email": row[2],
                    "role": row[3],
                    "display_name": row[4],
                    "mobile": row[5]
                }
            return None

        @staticmethod
        def AdminExists() -> bool:
            """
            التحقق من وجود مدير في النظام

            Returns:
                bool: True إذا كان هناك مدير واحد على الأقل
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")

            count = cursor.fetchone()[0]
            connection.close()

            return count > 0

    # ============================================================================
    # كلاس إدارة الأطباء
    # ============================================================================

    class DoctorManager:
        """
        إدارة الأطباء والمدرسين
        يحتوي على جميع العمليات المتعلقة بالأطباء
        """

        @staticmethod
        def AddDoctor(doctor_id: str, name: str, email: str, preferred_courses: str = "", time_availability: str = "") -> bool:
            """
            إضافة دكتور جديد

            Args:
                doctor_id: معرف الدكتور
                name: اسم الدكتور
                email: البريد الإلكتروني
                preferred_courses: المقررات المفضلة
                time_availability: أوقات التوفر

            Returns:
                bool: True إذا نجحت العملية
            """
            try:
                connection = DatabaseLayer.GetConnection()
                cursor = connection.cursor()

                cursor.execute('''
                    INSERT INTO doctors (doctor_id, name, email, preferred_courses, time_availability)
                    VALUES (?, ?, ?, ?, ?)
                ''', (doctor_id, name, email, preferred_courses, time_availability))

                connection.commit()
                return True

            except sqlite3.IntegrityError:
                # الدكتور موجود مسبقاً
                return False
            except Exception as e:
                print(f"خطأ في إضافة الدكتور: {e}")
                return False
            finally:
                connection.close()

        @staticmethod
        def GetAllDoctors() -> List[Dict]:
            """
            جلب جميع الأطباء

            Returns:
                List[Dict]: قائمة بجميع الأطباء
            """
            connection = DatabaseLayer.GetConnection()
            cursor = connection.cursor()

            cursor.execute('SELECT doctor_id, name, email, preferred_courses, time_availability FROM doctors ORDER BY name')

            doctors = []
            for row in cursor.fetchall():
                doctors.append({
                    "doctor_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "preferred_courses": row[3],
                    "time_availability": row[4]
                })

            connection.close()
            return doctors
