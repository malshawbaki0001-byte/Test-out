"""
================================================================================
Domain Models - طبقة الكائنات والمنطق
================================================================================

هذه الطبقة تحتوي على:
- الكلاسات الأساسية التي تمثل الكيانات (Course, Student, Section, User)
- المنطق والقوانين (التحقق من المتطلبات، التعارضات، السعة)
- لا تحتوي على استعلامات SQL مباشرة

المسؤوليات:
- تمثيل الكيانات الأساسية للنظام
- تطبيق القوانين والقيود
- التحقق من صحة البيانات
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime

class DomainModels:
    """كلاس الكائنات الأساسية والمنطق"""
    
    # ========================================================================
    # VALIDATORS
    # ========================================================================
    
    class LevelValidator:
        """مدقق المستوى"""
        MIN_LEVEL = 1
        MAX_LEVEL = 10
        
        @staticmethod
        def Validate(level: int) -> Tuple[bool, str]:
            """التحقق من صحة المستوى"""
            if not isinstance(level, int):
                return False, "Level must be an integer"
            if level < DomainModels.LevelValidator.MIN_LEVEL:
                return False, f"Level must be at least {DomainModels.LevelValidator.MIN_LEVEL}"
            if level > DomainModels.LevelValidator.MAX_LEVEL:
                return False, f"Level must be at most {DomainModels.LevelValidator.MAX_LEVEL}"
            return True, "Level is valid"
    
    # ========================================================================
    # DOMAIN MODELS
    # ========================================================================
    
    @dataclass
    class Course:
        """كلاس المقرر"""
        course_code: str
        name: str
        credits: int
        has_lab: bool
        level: int = 1
        prerequisites: List[str] = field(default_factory=list)

        def __post_init__(self):
            """التحقق من صحة البيانات"""
            if self.credits <= 0:
                raise ValueError("Credit hours must be positive")
        
        def CheckPrerequisites(self, student_transcript: List[str]) -> Tuple[bool, List[str]]:
            """
            التحقق من استيفاء المتطلبات السابقة
            
            Args:
                student_transcript: قائمة المقررات المجتازة للطالب
                
            Returns:
                tuple: (نجح/فشل, قائمة المتطلبات المفقودة)
            """
            missing = [prereq for prereq in self.prerequisites if prereq not in student_transcript]
            return len(missing) == 0, missing
        
        def IsAlreadyCompleted(self, student_transcript: List[str]) -> bool:
            """التحقق من أن المقرر لم يتم اجتيازه مسبقاً"""
            return self.course_code in student_transcript
    
    @dataclass
    class SectionSchedule:
        """جدول زمني للمحاضرة أو المختبر"""
        start_time: int
        end_time: int
        days: str
        hall: str

    @dataclass
    class Section:
        """كلاس الشعبة"""
        section_id: str
        course_code: str
        instructor: str
        max_capacity: int
        current_enrollment: int = 0
        lecture_schedule: Optional['DomainModels.SectionSchedule'] = None
        lab_schedule: Optional['DomainModels.SectionSchedule'] = None
        
        def IsFull(self) -> bool:
            """التحقق من أن الشعبة ممتلئة"""
            return self.current_enrollment >= self.max_capacity
        
        def HasTimeConflict(self, other: 'DomainModels.Section') -> bool:
            """
            التحقق من تعارض زمني مع شعبة أخرى

            Args:
                other: الشعبة الأخرى للتحقق من التعارض

            Returns:
                True إذا كان هناك تعارض
            """
            # التحقق من تعارض المحاضرات
            if self.lecture_schedule and other.lecture_schedule:
                if self._SchedulesOverlap(self.lecture_schedule, other.lecture_schedule):
                    return True

            # التحقق من تعارض المختبر
            if self.lab_schedule and other.lab_schedule:
                if self._SchedulesOverlap(self.lab_schedule, other.lab_schedule):
                    return True

            return False

        def _SchedulesOverlap(self, schedule1: 'DomainModels.SectionSchedule',
                             schedule2: 'DomainModels.SectionSchedule') -> bool:
            """التحقق من تعارض جدولين زمنيين"""
            # التحقق من الوقت
            time_conflict = not (schedule1.end_time <= schedule2.start_time or
                               schedule1.start_time >= schedule2.end_time)

            if not time_conflict:
                return False

            # التحقق من الأيام
            days1 = set(schedule1.days.split(',')) if schedule1.days else set()
            days2 = set(schedule2.days.split(',')) if schedule2.days else set()

            if not days1 or not days2:
                return True  # إذا لم يكن محدد، نفترض تعارض

            return bool(days1.intersection(days2))

        def GetLectureTimeString(self) -> str:
            """الحصول على نص وقت المحاضرة"""
            if self.lecture_schedule:
                return f"{self.lecture_schedule.start_time}:00 - {self.lecture_schedule.end_time}:00"
            return "لا يوجد"

        def GetLabTimeString(self) -> str:
            """الحصول على نص وقت المختبر"""
            if self.lab_schedule:
                return f"{self.lab_schedule.start_time}:00 - {self.lab_schedule.end_time}:00"
            return "لا يوجد"
    
    @dataclass
    class Student:
        """كلاس الطالب"""
        student_id: str
        name: str
        email: str
        program: str
        level: int
        transcript: List[str] = field(default_factory=list)
        schedule: List[Dict] = field(default_factory=list)
        
        def __post_init__(self):
            """التحقق من صحة البيانات"""
            allowed_programs = ['Computer', 'Comm', 'Communications', 'Power', 'Biomedical']
            if self.program not in allowed_programs:
                raise ValueError(f"Invalid program: {self.program}")
            validator = DomainModels.LevelValidator()
            is_valid, error_msg = validator.Validate(self.level)
            if not is_valid:
                raise ValueError(error_msg)
        
        def GetCompletedCredits(self, course_registry: Dict[str, 'DomainModels.Course']) -> int:
            """
            حساب الساعات المعتمدة المجتازة
            
            Args:
                course_registry: سجل المقررات
                
            Returns:
                عدد الساعات المعتمدة
            """
            total = 0
            for course_code in self.transcript:
                course = course_registry.get(course_code)
                if course:
                    total += course.credits
            return total
        
        def AddToTranscript(self, course_code: str):
            """إضافة مقرر إلى السجل الأكاديمي"""
            if course_code not in self.transcript:
                self.transcript.append(course_code)
        
        def IsRegisteredInCourse(self, course_code: str, section_registry: Dict[str, 'DomainModels.Section']) -> bool:
            """
            التحقق من أن الطالب مسجل في مقرر معين
            
            Args:
                course_code: رمز المقرر
                section_registry: سجل الشعب
                
            Returns:
                True إذا كان مسجلاً
            """
            for registration in self.schedule:
                section_id = registration.get('id')
                section = section_registry.get(section_id)
                if section and section.course_code == course_code:
                    return True
            return False
    
    @dataclass
    class User:
        """كلاس المستخدم"""
        user_id: str
        email: str
        password_hash: str
        role: str
        display_name: str = ""
        mobile: str = ""
        
        def IsAdmin(self) -> bool:
            """التحقق من أن المستخدم مدير"""
            return self.role == 'admin'
        
        def IsStudent(self) -> bool:
            """التحقق من أن المستخدم طالب"""
            return self.role == 'student'

        def IsDoctor(self) -> bool:
            """التحقق من أن المستخدم دكتور"""
            return self.role == 'doctor'

    @dataclass
    class Doctor:
        """كلاس الدكتور/الأستاذ"""
        doctor_id: str
        name: str
        email: str
        preferred_courses: str = ""
        time_availability: str = ""

        def GetPreferredCoursesList(self) -> List[str]:
            """
            جلب قائمة المقررات المفضلة كقائمة

            Returns:
                List[str]: قائمة برموز المقررات المفضلة
            """
            if not self.preferred_courses:
                return []
            return [course.strip() for course in self.preferred_courses.split(',') if course.strip()]

        def HasPreferredCourse(self, course_code: str) -> bool:
            """
            التحقق من أن المقرر من المقررات المفضلة

            Args:
                course_code: رمز المقرر

            Returns:
                bool: True إذا كان المقرر مفضلاً
            """
            return course_code in self.GetPreferredCoursesList()
    
    # ========================================================================
    # BUSINESS LOGIC
    # ========================================================================
    
    class RegistrationValidator:
        """مدقق التسجيل - يطبق قوانين التسجيل"""
        
        MIN_CREDITS = 12
        MAX_CREDITS = 18
        
        @staticmethod
        def ValidateRegistration(
            student: 'DomainModels.Student',
            section: 'DomainModels.Section',
            course: 'DomainModels.Course',
            course_registry: Dict[str, 'DomainModels.Course'],
            section_registry: Dict[str, 'DomainModels.Section'],
            current_registered_credits: int
        ) -> Tuple[bool, str]:
            """
            التحقق من صحة التسجيل في مقرر
            
            Args:
                student: الطالب
                course: المقرر
                section: الشعبة
                course_registry: سجل المقررات
                section_registry: سجل الشعب
                current_registered_credits: الساعات المسجلة حالياً
                
            Returns:
                tuple: (نجح/فشل, رسالة الخطأ)
            """
            # 1. التحقق من أن المقرر لم يتم اجتيازه
            if course.IsAlreadyCompleted(student.transcript):
                return False, f"المقرر {course.course_code} موجود في السجل الأكاديمي (تم اجتيازه مسبقاً)"
            
            # 2. التحقق من المتطلبات السابقة
            prereqs_met, missing = course.CheckPrerequisites(student.transcript)
            if not prereqs_met:
                return False, f"متطلبات سابقة غير مستوفاة: {', '.join(missing)}"
            
            # 3. التحقق من عدم التسجيل في نفس المقرر مرتين
            if student.IsRegisteredInCourse(course.course_code, section_registry):
                return False, f"مسجل بالفعل في المقرر {course.course_code}"
            
            # 4. التحقق من حدود الساعات المعتمدة
            new_total = current_registered_credits + course.credits
            if new_total > DomainModels.RegistrationValidator.MAX_CREDITS:
                return False, f"تجاوز الحد الأقصى: إضافة هذه المادة ({course.credits} ساعة) ستجعل مجموع الساعات ({new_total}) يتجاوز الحد الأقصى ({DomainModels.RegistrationValidator.MAX_CREDITS} ساعة)"
            
            # 5. التحقق من تعارض الأوقات
            for reg in student.schedule:
                existing_section_id = reg.get('id')
                existing_section = section_registry.get(existing_section_id)
                if existing_section and section.HasTimeConflict(existing_section):
                    return False, f"تعارض في الوقت مع {existing_section.section_id}"
            
            # 6. التحقق من السعة
            if section.IsFull():
                return False, f"الشعبة {section.section_id} ممتلئة"
            
            return True, "التسجيل صحيح"
        
        @staticmethod
        def ValidateCreditHours(registered_credits: int) -> Tuple[bool, str]:
            """
            التحقق من الساعات المسجلة
            
            Args:
                registered_credits: عدد الساعات المسجلة
                
            Returns:
                tuple: (صحيح/غير صحيح, رسالة)
            """
            if registered_credits < DomainModels.RegistrationValidator.MIN_CREDITS:
                return False, f"عدد الساعات المسجلة ({registered_credits}) أقل من الحد الأدنى المطلوب ({DomainModels.RegistrationValidator.MIN_CREDITS} ساعة)"
            if registered_credits > DomainModels.RegistrationValidator.MAX_CREDITS:
                return False, f"عدد الساعات المسجلة ({registered_credits}) يتجاوز الحد الأقصى ({DomainModels.RegistrationValidator.MAX_CREDITS} ساعة)"
            return True, "الساعات ضمن الحدود المسموحة"