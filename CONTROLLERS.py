"""
================================================================================
Controllers - طبقة التحكم
================================================================================

هذه الطبقة تعمل كجسر بين الواجهة الرسومية (GUI) وطبقة الكائنات (OOP).

المسؤوليات:
- استقبال طلبات من GUI
- استدعاء Domain Models و Database Layer
- إرجاع النتائج إلى GUI
- لا تحتوي على منطق معقد أو استعلامات SQL

التدفق: GUI → Controller → Domain Models → Database Layer
"""

from typing import List, Tuple, Optional, Dict
from datetime import datetime

from DATABASE_LAYER import DatabaseLayer
from DOMAIN_MODELS import DomainModels


class CourseController:
        """Controller للمقررات"""
        
        def __init__(self):
            self._course_cache: Dict[str, DomainModels.Course] = {}
            self._section_cache: Dict[str, DomainModels.Section] = {}
            self.RefreshCache()
        
        def RefreshCache(self):
            """تحديث التخزين المؤقت للمقررات والشعب"""
            data = DatabaseLayer.CourseRepository.FetchAllCoursesWithSections()
            self._course_cache.clear()
            self._section_cache.clear()
            
            for course_code, course_data in data.items():
                course = DomainModels.Course(
                    course_code=course_code,
                    name=course_data['name'],
                    credits=course_data['credit_hours'],
                    has_lab=course_data.get('has_lab', False),
                    level=course_data.get('level', 1),
                    prerequisites=course_data.get('prerequisites', [])
                )
                self._course_cache[course_code] = course
                
                for section_data in course_data.get('sections', []):
                    # إنشاء جدول المحاضرة إذا كان موجود
                    lecture_schedule = None
                    if section_data.get('lecture_start') and section_data.get('lecture_end'):
                        lecture_schedule = DomainModels.SectionSchedule(
                            start_time=section_data['lecture_start'],
                            end_time=section_data['lecture_end'],
                            days=section_data.get('lecture_days', ''),
                            hall=section_data.get('lecture_hall', section_data.get('hall', ''))
                        )

                    # إنشاء جدول المختبر إذا كان موجود
                    lab_schedule = None
                    if section_data.get('lab_start') and section_data.get('lab_end'):
                        lab_schedule = DomainModels.SectionSchedule(
                            start_time=section_data['lab_start'],
                            end_time=section_data['lab_end'],
                            days=section_data.get('lab_days', ''),
                            hall=section_data.get('lab_hall', section_data.get('hall', ''))
                        )

                    section = DomainModels.Section(
                        section_id=section_data['id'],
                        course_code=course_code,
                        instructor=section_data['instructor'],
                        max_capacity=section_data['max_capacity'],
                        current_enrollment=section_data.get('current_enrollment', 0),
                        lecture_schedule=lecture_schedule,
                        lab_schedule=lab_schedule
                    )
                    self._section_cache[section_data['id']] = section
        
        def GetCourse(self, course_code: str) -> Optional[DomainModels.Course]:
            """جلب مقرر"""
            return self._course_cache.get(course_code)
        
        def GetSection(self, section_id: str) -> Optional[DomainModels.Section]:
            """جلب شعبة"""
            return self._section_cache.get(section_id)
        
        def GetAllCourses(self) -> List[DomainModels.Course]:
            """جلب جميع المقررات"""
            return list(self._course_cache.values())
        
        def GetAvailableCourses(self, program: str, level: int) -> List[DomainModels.Course]:
            """جلب المقررات المتاحة لبرنامج ومستوى معين"""
            if program == 'Communications':
                program = 'Comm'
            filtered_courses = []
            for course in self._course_cache.values():
                if course.level == level:
                    filtered_courses.append(course)
            return sorted(filtered_courses, key=lambda c: c.course_code)
        
        def AddCourse(self, course: DomainModels.Course, prerequisites: List[str]) -> Tuple[bool, str]:
            """
            إضافة مقرر جديد
            
            Args:
                course: كائن المقرر
                prerequisites: قائمة المتطلبات السابقة
                
            Returns:
                tuple: (نجح/فشل, رسالة)
            """
            try:
                # التحقق من المتطلبات السابقة
                if prerequisites:
                    all_valid, invalid_codes = self.ValidatePrerequisites(prerequisites)
                    if not all_valid:
                        return False, f"المتطلب السابق '{invalid_codes[0]}' غير موجود في النظام."
                
                # حفظ في قاعدة البيانات
                DatabaseLayer.CourseRepository.InsertOrUpdateCourse(
                    course.course_code, course.name, course.credits,
                    course.has_lab, course.level
                )
                
                # حفظ المتطلبات السابقة
                if prerequisites:
                    DatabaseLayer.CourseRepository.SetPrerequisites(course.course_code, prerequisites)
                
                # تحديث التخزين المؤقت
                self.RefreshCache()
                return True, "تم حفظ المقرر بنجاح"
            except Exception as e:
                return False, f"فشل حفظ المقرر: {str(e)}"
        
        def DeleteCourse(self, course_code: str) -> Tuple[bool, str]:
            """حذف مقرر"""
            try:
                DatabaseLayer.CourseRepository.DeleteCourse(course_code)
                self.RefreshCache()
                return True, "تم حذف المقرر بنجاح"
            except Exception as e:
                return False, f"فشل حذف المقرر: {str(e)}"
        
        def ValidatePrerequisites(self, prereq_codes: List[str]) -> Tuple[bool, List[str]]:
            """التحقق من صحة المتطلبات السابقة"""
            missing_prereqs = []
            for prereq_code in prereq_codes:
                if not DatabaseLayer.CourseRepository.CourseExists(prereq_code):
                    missing_prereqs.append(prereq_code)
            return (True, []) if not missing_prereqs else (False, missing_prereqs)
        
        def AddSection(self, section: DomainModels.Section) -> Tuple[bool, str]:
            """إضافة شعبة"""
            try:
                # إعداد بيانات المحاضرة
                lecture_start = lecture_end = lecture_days = lecture_hall = None
                if section.lecture_schedule:
                    lecture_start = section.lecture_schedule.start_time
                    lecture_end = section.lecture_schedule.end_time
                    lecture_days = section.lecture_schedule.days
                    lecture_hall = section.lecture_schedule.hall

                # إعداد بيانات المختبر
                lab_start = lab_end = lab_days = lab_hall = None
                if section.lab_schedule:
                    lab_start = section.lab_schedule.start_time
                    lab_end = section.lab_schedule.end_time
                    lab_days = section.lab_schedule.days
                    lab_hall = section.lab_schedule.hall

                DatabaseLayer.CourseRepository.InsertOrUpdateSection(
                    section.section_id, section.course_code, section.instructor,
                    lecture_start, lecture_end, lecture_days, lecture_hall,
                    lab_start, lab_end, lab_days, lab_hall,
                    section.max_capacity, section.current_enrollment
                )
                self.RefreshCache()
                return True, "تم حفظ الشعبة بنجاح"
            except Exception as e:
                return False, f"فشل حفظ الشعبة: {str(e)}"
        
        def DeleteSection(self, section_id: str) -> Tuple[bool, str]:
            """حذف شعبة"""
            try:
                DatabaseLayer.CourseRepository.DeleteSection(section_id)
                self.RefreshCache()
                return True, "تم حذف الشعبة بنجاح"
            except Exception as e:
                return False, f"فشل حذف الشعبة: {str(e)}"
    
    # ========================================================================
    # STUDENT CONTROLLER
    # ========================================================================
    
    class StudentController:
        """Controller للطلاب"""
        
        def __init__(self, course_controller: 'Controllers.CourseController'):
            self.course_controller = course_controller
        
        def GetStudent(self, student_id: str) -> Optional[DomainModels.Student]:
            """جلب بيانات طالب"""
            student_data = DatabaseLayer.StudentRepository.GetStudentData(student_id)
            if not student_data:
                return None
            
            student_id, name, email, program, level = student_data
            
            # جلب السجل الأكاديمي
            transcript_data = DatabaseLayer.StudentRepository.GetTranscript(student_id)
            transcript = [row[0] for row in transcript_data]
            
            # إضافة المواد من المستويات السابقة
            if level > 1:
                program_for_query = program
                for prev_level in range(1, level):
                    courses_for_level = DatabaseLayer.CourseRepository.GetAllCourseCodes()
                    for course_code in courses_for_level:
                        if course_code not in transcript:
                            DatabaseLayer.StudentRepository.AddCourseToTranscript(student_id, course_code)
                            transcript.append(course_code)
            
            # جلب التسجيلات
            registrations = DatabaseLayer.RegistrationRepository.GetStudentRegistrations(student_id)
            schedule = [{"id": row[0], "registration_time": row[1]} for row in registrations]
            
            # تحويل 'Comm' إلى 'Communications'
            if program == 'Comm':
                program = 'Communications'
            
            return DomainModels.Student(
                student_id=student_id,
                name=name,
                email=email,
                program=program,
                level=level,
                transcript=transcript,
                schedule=schedule
            )
        
        def AddStudent(self, student_id: str, name: str, email: str, program: str, level: int) -> Tuple[bool, str]:
            """إضافة طالب جديد"""
            if program == 'Communications':
                program = 'Comm'
            if program not in DatabaseLayer.ALLOWED_PROGRAMS:
                return False, "❌ Please select a valid program."
            
            if DatabaseLayer.StudentRepository.StudentExists(student_id):
                return False, "❌ Student ID already exists."
            
            try:
                DatabaseLayer.StudentRepository.InsertStudent(student_id, name, email, program, level)
                return True, "✅ Student registered successfully!"
            except Exception as e:
                return False, f"❌ Error: {str(e)}"
        
        def DeleteStudent(self, student_id: str) -> Tuple[bool, str]:
            """حذف طالب"""
            try:
                DatabaseLayer.StudentRepository.DeleteStudent(student_id)
                return True, "تم حذف الطالب بنجاح"
            except Exception as e:
                return False, f"فشل حذف الطالب: {str(e)}"
        
        def GetAllStudents(self) -> List[Tuple]:
            """جلب جميع الطلاب"""
            return DatabaseLayer.StudentRepository.GetAllStudents()
        
        def RegisterStudent(self, student: DomainModels.Student, section_id: str) -> Tuple[bool, str]:
            """
            تسجيل طالب في شعبة
            
            Args:
                student: كائن الطالب
                section_id: معرف الشعبة
                
            Returns:
                tuple: (نجح/فشل, رسالة)
            """
            section = self.course_controller.GetSection(section_id)
            if not section:
                return False, f"Section {section_id} not found"
            
            course = self.course_controller.GetCourse(section.course_code)
            if not course:
                return False, f"Course {section.course_code} not found"
            
            # حساب الساعات المسجلة حالياً
            current_registered_credits = 0
            for reg in student.schedule:
                reg_section = self.course_controller.GetSection(reg.get('id'))
                if reg_section:
                    reg_course = self.course_controller.GetCourse(reg_section.course_code)
                    if reg_course:
                        current_registered_credits += reg_course.credits
            
            # التحقق من صحة التسجيل
            is_valid, error_msg = DomainModels.RegistrationValidator.ValidateRegistration(
                student, section, course,
                self.course_controller._course_cache,
                self.course_controller._section_cache,
                current_registered_credits
            )
            
            if not is_valid:
                return False, error_msg
            
            # تنفيذ التسجيل
            try:
                # تحديث عدد المسجلين
                success, error = DatabaseLayer.CourseRepository.UpdateSectionEnrollment(section_id, increment=True)
                if not success:
                    return False, error
                
                # إضافة التسجيل
                registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                DatabaseLayer.RegistrationRepository.InsertRegistration(
                    student.student_id, section_id, registration_time
                )
                
                # تحديث كائن الطالب
                student.schedule.append({"id": section_id, "registration_time": registration_time})
                
                return True, "تم التسجيل بنجاح"
            except Exception as e:
                return False, f"فشل التسجيل: {str(e)}"
        
        def UnregisterStudent(self, student: DomainModels.Student, section_id: str) -> Tuple[bool, str]:
            """إلغاء تسجيل طالب من شعبة"""
            try:
                DatabaseLayer.RegistrationRepository.DeleteRegistration(student.student_id, section_id)
                DatabaseLayer.CourseRepository.UpdateSectionEnrollment(section_id, increment=False)
                student.schedule = [reg for reg in student.schedule if reg.get('id') != section_id]
                return True, "تم إلغاء التسجيل بنجاح"
            except Exception as e:
                return False, f"فشل إلغاء التسجيل: {str(e)}"
    
    # ========================================================================
    # USER CONTROLLER
    # ========================================================================
    
    class UserController:
        """Controller للمستخدمين"""
        
        def Authenticate(self, identifier: str, password: str) -> Optional[DomainModels.User]:
            """
            المصادقة - التحقق من بيانات المستخدم
            
            Args:
                identifier: المعرف (user_id, student_id, أو email)
                password: كلمة المرور
                
            Returns:
                كائن المستخدم إذا نجحت المصادقة، None إذا فشلت
            """
            import bcrypt
            import hashlib
            
            user_data = DatabaseLayer.UserRepository.GetUserByIdentifier(identifier)
            if not user_data:
                return None
            
            user_id, student_id, email, password_hash, role, display_name, mobile = user_data
            
            if not password_hash:
                return None
            
            # التحقق من كلمة المرور
            try:
                password_match = False
                
                # التحقق من bcrypt
                if isinstance(password_hash, str) and password_hash.startswith('$2b$'):
                    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                        password_match = True
                
                # دعم التنسيقات القديمة
                elif isinstance(password_hash, str):
                    if password_hash == password:
                        password_match = True
                    else:
                        sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                        if password_hash == sha256_hash:
                            password_match = True
                
                if password_match:
                    final_user_id = str(student_id) if student_id else str(user_id)
                    return DomainModels.User(
                        user_id=final_user_id,
                        email=email,
                        password_hash=password_hash,
                        role=role or 'student',
                        display_name=display_name or '',
                        mobile=mobile or ''
                    )
            except (ValueError, TypeError) as e:
                print(f"Error checking password: {e}")
                return None
            
            return None
        
        def CreateUser(self, user_id: str, email: str, password: str, role: str,
                       display_name: str = "", mobile: str = "") -> Tuple[bool, str]:
            """إنشاء مستخدم جديد"""
            import bcrypt
            
            if len(password) < 8:
                return False, "Password must be at least 8 characters"
            
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            try:
                student_id_value = None if role == 'admin' else user_id
                DatabaseLayer.UserRepository.InsertUser(
                    student_id_value, email, password_hash, role, display_name, mobile
                )
                return True, "User created successfully"
            except Exception as e:
                return False, str(e)
        
        def CreateDefaultAdmin(self) -> Tuple[bool, str]:
            """إنشاء حساب مدير افتراضي"""
            if DatabaseLayer.UserRepository.AdminExists():
                return False, "Admin already exists"
            
            import bcrypt
            admin_email = "admin@system.com"
            admin_password = "Admin1234"
            password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            try:
                DatabaseLayer.UserRepository.InsertUser(
                    None, admin_email, password_hash, 'admin', 'System Admin', ''
                )
                return True, f"Default admin created. Email: {admin_email}, Password: {admin_password}"
            except Exception as e:
                return False, str(e)
    
    # ========================================================================
    # DOCTOR CONTROLLER
    # ========================================================================
    
    class DoctorController:
        """Controller لأعضاء هيئة التدريس"""
        
        def __init__(self, course_controller: 'Controllers.CourseController'):
            self.course_controller = course_controller
        
        def GetAllDoctors(self) -> List[Tuple]:
            """جلب جميع أعضاء هيئة التدريس"""
            return DatabaseLayer.DoctorRepository.GetDoctor()
        
        def GetDoctor(self, doctor_id: str) -> Optional[Tuple]:
            """جلب عضو هيئة تدريس"""
            return DatabaseLayer.DoctorRepository.GetDoctor(doctor_id)
        
        def AddDoctor(self, doctor_id: str, name: str, email: str,
                      preferred_courses: str = '', time_availability: str = '') -> Tuple[bool, str]:
            """إضافة عضو هيئة تدريس"""
            try:
                DatabaseLayer.DoctorRepository.InsertOrUpdateDoctor(
                    doctor_id, name, email, preferred_courses, time_availability
                )
                return True, "تم حفظ Doctor بنجاح"
            except Exception as e:
                return False, f"فشل حفظ Doctor: {str(e)}"
        
        def DeleteDoctor(self, doctor_id: str) -> Tuple[bool, str]:
            """حذف عضو هيئة تدريس"""
            try:
                DatabaseLayer.DoctorRepository.DeleteDoctor(doctor_id)
                return True, "تم حذف Doctor بنجاح"
            except Exception as e:
                return False, f"فشل حذف Doctor: {str(e)}"
        
        def AssignCourse(self, doctor_id: str, course_code: str, section_id: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
            """
            تعيين مقرر لعضو هيئة تدريس
            
            Returns:
                tuple: (نجح/فشل, رسالة, assignment_id)
            """
            try:
                section = self.course_controller.GetSection(section_id) if section_id else None
                
                # التحقق من التعارضات الزمنية
                if section:
                    has_conflict = DatabaseLayer.DoctorRepository.CheckTimeConflict(
                        doctor_id, section.start_time, section.end_time
                    )
                    if has_conflict:
                        # إرجاع تحذير لكن السماح بالتعيين
                        assignment_id = DatabaseLayer.DoctorRepository.InsertAssignment(doctor_id, course_code, section_id)
                        return True, "تم التعيين بنجاح (مع تحذير: يوجد تعارض زمني)", assignment_id
                
                assignment_id = DatabaseLayer.DoctorRepository.InsertAssignment(doctor_id, course_code, section_id)
                return True, "تم تعيين المقرر بنجاح", assignment_id
            except Exception as e:
                return False, f"فشل التعيين: {str(e)}", None
        
        def RemoveAssignment(self, assignment_id: int) -> Tuple[bool, str]:
            """إزالة تعيين"""
            try:
                DatabaseLayer.DoctorRepository.DeleteAssignment(assignment_id)
                return True, "تم إزالة التعيين بنجاح"
            except Exception as e:
                return False, f"فشل الإزالة: {str(e)}"
        
        def GetAssignments(self, doctor_id: str) -> List[Tuple]:
            """جلب تعيينات عضو هيئة تدريس"""
            return DatabaseLayer.DoctorRepository.GetAssignments(doctor_id)
        
        def GetSchedule(self, doctor_id: str) -> List[Dict]:
            """جلب الجدول الزمني لعضو هيئة تدريس"""
            return DatabaseLayer.DoctorRepository.GetDoctorSchedule(doctor_id)
        
        def CheckTimeConflict(self, doctor_id: str, start_time: int, end_time: int,
                               exclude_section_id: Optional[str] = None) -> bool:
            """التحقق من تعارض زمني"""
            return DatabaseLayer.DoctorRepository.CheckTimeConflict(
                doctor_id, start_time, end_time, exclude_section_id
            )

        def CreateDefaultDoctor(self) -> Tuple[bool, str]:
            """إنشاء حساب دكتور افتراضي للاختبار"""
            # فحص إذا كان هناك دكتور افتراضي موجود
            doctors = self.GetAllDoctors()
            if doctors:
                return False, "Doctor already exists"

            import bcrypt
            doctor_email = "doctor@system.com"
            doctor_password = "Doctor1234"
            password_hash = bcrypt.hashpw(doctor_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            try:
                # إضافة الدكتور في جدول doctors
                DatabaseLayer.DoctorRepository.InsertOrUpdateDoctor(
                    "DOC001", "د. أحمد محمد", doctor_email,
                    "EE202,CS301,MATH101", "الأحد 8-10، الثلاثاء 2-4"
                )

                # إضافة المستخدم في جدول users
                DatabaseLayer.UserRepository.InsertUser(
                    "DOC001", doctor_email, password_hash, 'doctor', 'د. أحمد محمد', ''
                )

                return True, f"Default doctor created. Email: {doctor_email}, Password: {doctor_password}"
            except Exception as e:
                return False, str(e)