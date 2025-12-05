"""Admin Module - لوحة تحكم المدير"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QLineEdit, QFormLayout, QComboBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from CONTROLLERS import CourseController, StudentController, DoctorController
from DOMAIN_MODELS import DomainModels
from STUDENT_MODULE import DashboardBase
from APP_MODULE import AppModule


class AdminDashboard(DashboardBase):
    def __init__(self, user: DomainModels.User):
        super().__init__()
        self.user = user
        self.course_controller = Controllers.CourseController()
        self.student_controller = Controllers.StudentController(self.course_controller)
        self.doctor_controller = Controllers.DoctorController(self.course_controller)
        self.setWindowTitle(f'لوحة تحكم المدير - {user.display_name}')
        self.setGeometry(100, 100, 1100, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.InitUi()
        self.LoadData()
    
    def InitUi(self):
        layout = QVBoxLayout(self)
        top_bar = QHBoxLayout()
        self.theme_button = QPushButton("🌙")
        self.theme_button.setProperty("class", "theme_button")
        self.theme_button.clicked.connect(self.ToggleTheme)
        self.signout_button = QPushButton("تسجيل الخروج")
        self.signout_button.setProperty("class", "secondary")
        self.signout_button.clicked.connect(self.HandleSignout)
        top_bar.addWidget(self.theme_button)
        top_bar.addWidget(self.signout_button)
        top_bar.addStretch()
        layout.addLayout(top_bar)
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.CreateCoursesTab(), "المقررات")
        self.tab_widget.addTab(self.CreateSectionsTab(), "الشعب")
        self.tab_widget.addTab(self.CreateDoctorsTab(), "الدكاترة")
        self.tab_widget.addTab(self.CreateUsersTab(), "المستخدمون")
        layout.addWidget(self.tab_widget)
    
    def CreateCoursesTab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._CreateCoursesListPanel(), 1)
        main_layout.addWidget(self._CreateCoursesFormPanel(), 1)
        layout.addLayout(main_layout)
        return widget
    
    def _CreateCoursesListPanel(self) -> QFrame:
        frame = self._CreateCardFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("قائمة المقررات"))
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(5)
        self.courses_table.setHorizontalHeaderLabels(['رمز المادة', 'اسم المادة', 'الساعات', 'المحاضرات', 'المستوى'])
        self.courses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.courses_table.itemSelectionChanged.connect(self.OnCourseSelected)
        layout.addWidget(self.courses_table)
        delete_button = QPushButton("حذف المقرر المحدد")
        delete_button.setProperty("class", "danger")
        delete_button.clicked.connect(self.HandleDeleteCourse)
        layout.addWidget(delete_button)
        return frame
    
    def _CreateCoursesFormPanel(self) -> QFrame:
        frame = self._CreateCardFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("إضافة/تحديث مقرر"))
        form_layout = QFormLayout()
        self.course_code_input = QLineEdit()
        self.course_code_input.setPlaceholderText("مثال: EE202")
        self.course_name_input = QLineEdit()
        self.course_name_input.setPlaceholderText("اسم المقرر")
        self.course_credits_input = QLineEdit()
        self.course_credits_input.setPlaceholderText("الساعات المعتمدة")
        self.course_has_lab_input = QComboBox()
        self.course_has_lab_input.addItems(["لا", "نعم"])
        self.course_has_lab_input.setToolTip("هل المادة تحتوي على مختبر؟")
        self.course_level_input = QComboBox()
        self.course_level_input.addItems([str(i) for i in range(1, 11)])
        self.course_prerequisites_input = QLineEdit()
        self.course_prerequisites_input.setPlaceholderText("المتطلبات السابقة (مفصولة بفواصل)")
        form_layout.addRow('رمز المقرر:', self.course_code_input)
        form_layout.addRow('اسم المقرر:', self.course_name_input)
        form_layout.addRow('الساعات المعتمدة:', self.course_credits_input)
        form_layout.addRow('يحتوي على مختبر:', self.course_has_lab_input)
        form_layout.addRow('المستوى:', self.course_level_input)
        form_layout.addRow('المتطلبات السابقة:', self.course_prerequisites_input)
        layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("حفظ المقرر")
        save_button.clicked.connect(self.HandleSaveCourse)
        clear_button = QPushButton("مسح النموذج")
        clear_button.setProperty("class", "secondary")
        clear_button.clicked.connect(self.ClearCourseForm)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(clear_button)
        layout.addLayout(buttons_layout)
        return frame
    
    def CreateSectionsTab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._CreateSectionsListPanel(), 1)
        main_layout.addWidget(self._CreateSectionsFormPanel(), 1)
        layout.addLayout(main_layout)
        return widget
    
    def _CreateSectionsListPanel(self) -> QFrame:
        frame = self._CreateCardFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("قائمة الشعب"))
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("اختر مقرر:"))
        self.sections_course_combo = QComboBox()
        self.sections_course_combo.currentTextChanged.connect(self.OnSectionsCourseChanged)
        course_layout.addWidget(self.sections_course_combo)
        layout.addLayout(course_layout)
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(7)
        self.sections_table.setHorizontalHeaderLabels(['ID الشعبة', 'المدرس', 'وقت المحاضرة', 'وقت المختبر', 'السعة', 'المسجلين', 'المعرف'])
        self.sections_table.setColumnHidden(7, True)
        self.sections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sections_table.itemSelectionChanged.connect(self.OnSectionSelected)
        layout.addWidget(self.sections_table)
        delete_button = QPushButton("حذف الشعبة المحددة")
        delete_button.setProperty("class", "danger")
        delete_button.clicked.connect(self.HandleDeleteSection)
        layout.addWidget(delete_button)
        return frame
    
    def _CreateSectionsFormPanel(self) -> QFrame:
        frame = self._CreateCardFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("إضافة/تحديث شعبة"))
        form_layout = QFormLayout()

        # الحقول الأساسية
        self.section_id_input = QLineEdit()
        self.section_id_input.setPlaceholderText("مثال: EE202-01")
        self.section_course_combo = QComboBox()
        self.section_course_combo.currentTextChanged.connect(self.OnCourseChanged)
        self.section_instructor_input = QLineEdit()
        self.section_instructor_input.setPlaceholderText("اسم المدرس")
        self.section_capacity_input = QLineEdit()
        self.section_capacity_input.setPlaceholderText("السعة القصوى")

        form_layout.addRow('معرف الشعبة:', self.section_id_input)
        form_layout.addRow('المقرر:', self.section_course_combo)
        form_layout.addRow('المدرس:', self.section_instructor_input)
        form_layout.addRow('السعة القصوى:', self.section_capacity_input)

        # قسم المحاضرة
        lecture_group = QGroupBox("جدول المحاضرة")
        lecture_layout = QFormLayout(lecture_group)
        self.lecture_start_time_combo = QComboBox()
        self.lecture_start_time_combo.addItems([f"{i}:00" for i in range(8, 22)])
        self.lecture_end_time_combo = QComboBox()
        self.lecture_end_time_combo.addItems([f"{i}:00" for i in range(8, 22)])
        self.lecture_days_input = QLineEdit()
        self.lecture_days_input.setPlaceholderText("الأيام (مفصولة بفواصل)")
        self.lecture_hall_input = QLineEdit()
        self.lecture_hall_input.setPlaceholderText("قاعة المحاضرة")

        lecture_layout.addRow('وقت البداية:', self.lecture_start_time_combo)
        lecture_layout.addRow('وقت النهاية:', self.lecture_end_time_combo)
        lecture_layout.addRow('الأيام:', self.lecture_days_input)
        lecture_layout.addRow('القاعة:', self.lecture_hall_input)
        layout.addWidget(lecture_group)

        # قسم المختبر (سيظهر ديناميكياً)
        self.lab_group = QGroupBox("جدول المختبر")
        self.lab_group.setVisible(False)  # مخفي افتراضياً
        lab_layout = QFormLayout(self.lab_group)
        self.lab_start_time_combo = QComboBox()
        self.lab_start_time_combo.addItems([f"{i}:00" for i in range(8, 22)])
        self.lab_end_time_combo = QComboBox()
        self.lab_end_time_combo.addItems([f"{i}:00" for i in range(8, 22)])
        self.lab_days_input = QLineEdit()
        self.lab_days_input.setPlaceholderText("الأيام (مفصولة بفواصل)")
        self.lab_hall_input = QLineEdit()
        self.lab_hall_input.setPlaceholderText("قاعة المختبر")

        lab_layout.addRow('وقت البداية:', self.lab_start_time_combo)
        lab_layout.addRow('وقت النهاية:', self.lab_end_time_combo)
        lab_layout.addRow('الأيام:', self.lab_days_input)
        lab_layout.addRow('القاعة:', self.lab_hall_input)
        layout.addWidget(self.lab_group)

        layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("حفظ الشعبة")
        save_button.clicked.connect(self.HandleSaveSection)
        clear_button = QPushButton("مسح النموذج")
        clear_button.setProperty("class", "secondary")
        clear_button.clicked.connect(self.ClearSectionForm)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(clear_button)
        layout.addLayout(buttons_layout)
        return frame
    
    def CreateUsersTab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self._CreateUsersListPanel())
        return widget
    
    def _CreateUsersListPanel(self) -> QFrame:
        frame = self._CreateCardFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("قائمة الطلاب"))
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(['المعرف', 'الاسم', 'البريد', 'البرنامج', 'المستوى'])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.students_table)
        delete_button = QPushButton("حذف الطالب المحدد")
        delete_button.setProperty("class", "danger")
        delete_button.clicked.connect(self.HandleDeleteStudent)
        layout.addWidget(delete_button)
        return frame
    
    def _CreateCardFrame(self) -> QFrame:
        frame = QFrame()
        frame.setProperty("class", "card")
        AppModule.ApplyShadow(frame)
        return frame
    
    def LoadData(self):
        self.course_controller.RefreshCache()
        self.LoadCourses()
        self.LoadStudents()
        self.LoadSectionsCourses()
        self.UpdateSectionsCombo("")
    
    def LoadCourses(self):
        self.courses_table.setRowCount(0)
        for i, course in enumerate(self.course_controller.GetAllCourses()):
            self.courses_table.insertRow(i)
            self.courses_table.setItem(i, 0, QTableWidgetItem(course.course_code))
            self.courses_table.setItem(i, 1, QTableWidgetItem(course.name))
            self.courses_table.setItem(i, 2, QTableWidgetItem(str(course.credits)))
            self.courses_table.setItem(i, 3, QTableWidgetItem("نعم" if course.has_lab else "لا"))
            self.courses_table.setItem(i, 4, QTableWidgetItem(str(course.level)))
    
    def LoadStudents(self):
        self.students_table.setRowCount(0)
        students = self.student_controller.GetAllStudents()
        for i, student in enumerate(students):
            self.students_table.insertRow(i)
            self.students_table.setItem(i, 0, QTableWidgetItem(str(student[0])))
            self.students_table.setItem(i, 1, QTableWidgetItem(student[1]))
            self.students_table.setItem(i, 2, QTableWidgetItem(student[2]))
            self.students_table.setItem(i, 3, QTableWidgetItem(student[3]))
            self.students_table.setItem(i, 4, QTableWidgetItem(str(student[4])))
    
    def HandleSaveCourse(self):
        course_code = self.course_code_input.text().strip()
        name = self.course_name_input.text().strip()
        credits_text = self.course_credits_input.text().strip()
        has_lab = self.course_has_lab_input.currentText() == "نعم"
        level = int(self.course_level_input.currentText())
        prerequisites_text = self.course_prerequisites_input.text().strip()

        if not course_code or not name or not credits_text:
            QMessageBox.warning(self, "خطأ", "الرجاء ملء جميع الحقول المطلوبة")
            return

        try:
            credits = int(credits_text)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "الساعات المعتمدة يجب أن تكون رقماً")
            return

        prerequisites = [p.strip() for p in prerequisites_text.split(',') if p.strip()]
        course = DomainModels.Course(
            course_code=course_code,
            name=name,
            credits=credits,
            has_lab=has_lab,
            level=level,
            prerequisites=prerequisites
        )
        
        success, message = self.course_controller.AddCourse(course, prerequisites)
        if success:
            QMessageBox.information(self, "نجح", message)
            self.ClearCourseForm()
            self.LoadData()
        else:
            QMessageBox.warning(self, "خطأ", message)
    
    def ClearCourseForm(self):
        self.course_code_input.clear()
        self.course_name_input.clear()
        self.course_credits_input.clear()
        self.course_has_lab_input.setCurrentIndex(0)
        self.course_level_input.setCurrentIndex(0)
        self.course_prerequisites_input.clear()
    
    def OnCourseSelected(self):
        row = self.courses_table.currentRow()
        if row >= 0:
            course_code = self.courses_table.item(row, 0).text()
            course = self.course_controller.GetCourse(course_code)
            if course:
                self.course_code_input.setText(course.course_code)
                self.course_name_input.setText(course.name)
                self.course_credits_input.setText(str(course.credits))
                self.course_has_lab_input.setCurrentText("نعم" if course.has_lab else "لا")
                self.course_level_input.setCurrentText(str(course.level))
                self.course_prerequisites_input.setText(', '.join(course.prerequisites))
    
    def HandleDeleteCourse(self):
        row = self.courses_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار مقرر أولاً")
            return
        
        course_code = self.courses_table.item(row, 0).text()
        reply = QMessageBox.question(self, 'تأكيد الحذف', f'هل أنت متأكد من حذف المقرر {course_code}؟',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.course_controller.DeleteCourse(course_code)
            if success:
                QMessageBox.information(self, "نجح", message)
                self.LoadData()
            else:
                QMessageBox.warning(self, "خطأ", message)
    
    def LoadSectionsCourses(self):
        self.sections_course_combo.clear()
        self.sections_course_combo.addItem("جميع المقررات", "")
        for course in self.course_controller.GetAllCourses():
            self.sections_course_combo.addItem(f"{course.course_code} - {course.name}", course.course_code)
    
    def LoadSections(self, course_code: str = None):
        self.sections_table.setRowCount(0)
        sections = list(self.course_controller._section_cache.values())
        if course_code:
            sections = [s for s in sections if s.course_code == course_code]

        for i, section in enumerate(sections):
            self.sections_table.insertRow(i)
            self.sections_table.setItem(i, 0, QTableWidgetItem(section.section_id))
            self.sections_table.setItem(i, 1, QTableWidgetItem(section.instructor))
            self.sections_table.setItem(i, 2, QTableWidgetItem(section.GetLectureTimeString()))
            self.sections_table.setItem(i, 3, QTableWidgetItem(section.GetLabTimeString()))
            self.sections_table.setItem(i, 4, QTableWidgetItem(str(section.max_capacity)))
            self.sections_table.setItem(i, 5, QTableWidgetItem(str(section.current_enrollment)))
            self.sections_table.setItem(i, 6, QTableWidgetItem(section.section_id))
    
    def OnCourseChanged(self, course_code: str):
        """عند تغيير المقرر، إظهار/إخفاء قسم المختبر"""
        if course_code:
            course = self.course_controller.GetCourse(course_code)
            if course and course.has_lab:
                self.lab_group.setVisible(True)
            else:
                self.lab_group.setVisible(False)
        else:
            self.lab_group.setVisible(False)

    def OnSectionsCourseChanged(self, course_code: str):
        self.LoadSections(course_code if course_code else None)
    
    def OnSectionSelected(self):
        row = self.sections_table.currentRow()
        if row >= 0:
            section_id = self.sections_table.item(row, 6).text()
            section = self.course_controller.GetSection(section_id)
            if section:
                self.section_id_input.setText(section.section_id)
                self.section_course_combo.setCurrentText(section.course_code)
                self.section_instructor_input.setText(section.instructor)
                self.section_capacity_input.setText(str(section.max_capacity))

                # تعبئة بيانات المحاضرة
                if section.lecture_schedule:
                    self.lecture_start_time_combo.setCurrentText(f"{section.lecture_schedule.start_time}:00")
                    self.lecture_end_time_combo.setCurrentText(f"{section.lecture_schedule.end_time}:00")
                    self.lecture_days_input.setText(section.lecture_schedule.days or "")
                    self.lecture_hall_input.setText(section.lecture_schedule.hall or "")

                # تعبئة بيانات المختبر
                if section.lab_schedule:
                    self.lab_start_time_combo.setCurrentText(f"{section.lab_schedule.start_time}:00")
                    self.lab_end_time_combo.setCurrentText(f"{section.lab_schedule.end_time}:00")
                    self.lab_days_input.setText(section.lab_schedule.days or "")
                    self.lab_hall_input.setText(section.lab_schedule.hall or "")
                    self.lab_group.setVisible(True)
                else:
                    self.lab_group.setVisible(False)

                # تحديث رؤية قسم المختبر بناءً على المقرر
                course = self.course_controller.GetCourse(section.course_code)
                if course and course.has_lab:
                    self.lab_group.setVisible(True)
                else:
                    self.lab_group.setVisible(False)
    
    
    def HandleSaveSection(self):
        section_id = self.section_id_input.text().strip()
        course_code = self.section_course_combo.currentText()
        instructor = self.section_instructor_input.text().strip()
        capacity_text = self.section_capacity_input.text().strip()

        if not section_id or not course_code or not instructor or not capacity_text:
            QMessageBox.warning(self, "خطأ", "الرجاء ملء جميع الحقول المطلوبة")
            return

        try:
            capacity = int(capacity_text)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "السعة يجب أن تكون رقماً")
            return

        # إنشاء جدول المحاضرة
        lecture_start_text = self.lecture_start_time_combo.currentText()
        lecture_end_text = self.lecture_end_time_combo.currentText()
        lecture_days = self.lecture_days_input.text().strip()
        lecture_hall = self.lecture_hall_input.text().strip()

        if not lecture_start_text or not lecture_end_text or not lecture_days or not lecture_hall:
            QMessageBox.warning(self, "خطأ", "الرجاء ملء جميع بيانات المحاضرة")
            return

        try:
            lecture_start = int(lecture_start_text.split(':')[0])
            lecture_end = int(lecture_end_text.split(':')[0])
        except ValueError:
            QMessageBox.warning(self, "خطأ", "أوقات المحاضرة يجب أن تكون صحيحة")
            return

        lecture_schedule = DomainModels.SectionSchedule(
            start_time=lecture_start,
            end_time=lecture_end,
            days=lecture_days,
            hall=lecture_hall
        )

        # إنشاء جدول المختبر (إذا كان المقرر يحتوي على مختبر)
        lab_schedule = None
        course = self.course_controller.GetCourse(course_code)
        if course and course.has_lab:
            lab_start_text = self.lab_start_time_combo.currentText()
            lab_end_text = self.lab_end_time_combo.currentText()
            lab_days = self.lab_days_input.text().strip()
            lab_hall = self.lab_hall_input.text().strip()

            if not lab_start_text or not lab_end_text or not lab_days or not lab_hall:
                QMessageBox.warning(self, "خطأ", "الرجاء ملء جميع بيانات المختبر")
                return

            try:
                lab_start = int(lab_start_text.split(':')[0])
                lab_end = int(lab_end_text.split(':')[0])
            except ValueError:
                QMessageBox.warning(self, "خطأ", "أوقات المختبر يجب أن تكون صحيحة")
                return

            lab_schedule = DomainModels.SectionSchedule(
                start_time=lab_start,
                end_time=lab_end,
                days=lab_days,
                hall=lab_hall
            )

        section = DomainModels.Section(
            section_id=section_id,
            course_code=course_code,
            instructor=instructor,
            max_capacity=capacity,
            lecture_schedule=lecture_schedule,
            lab_schedule=lab_schedule
        )
        
        success, message = self.course_controller.AddSection(section)
        if success:
            QMessageBox.information(self, "نجح", message)
            self.ClearSectionForm()
            self.LoadData()
        else:
            QMessageBox.warning(self, "خطأ", message)
    
    def ClearSectionForm(self):
        self.section_id_input.clear()
        self.section_course_combo.setCurrentIndex(0)
        self.section_instructor_input.clear()
        self.section_capacity_input.clear()
        self.lecture_start_time_combo.setCurrentIndex(0)
        self.lecture_end_time_combo.setCurrentIndex(0)
        self.lecture_days_input.clear()
        self.lecture_hall_input.clear()
        self.lab_start_time_combo.setCurrentIndex(0)
        self.lab_end_time_combo.setCurrentIndex(0)
        self.lab_days_input.clear()
        self.lab_hall_input.clear()
        self.lab_group.setVisible(False)
    
    def HandleDeleteSection(self):
        row = self.sections_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار شعبة أولاً")
            return
        
        section_id = self.sections_table.item(row, 6).text()
        reply = QMessageBox.question(self, 'تأكيد الحذف', f'هل أنت متأكد من حذف الشعبة {section_id}؟',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.course_controller.DeleteSection(section_id)
            if success:
                QMessageBox.information(self, "نجح", message)
                self.LoadData()
            else:
                QMessageBox.warning(self, "خطأ", message)
    
    def HandleDeleteStudent(self):
        row = self.students_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار طالب أولاً")
            return
        
        student_id = self.students_table.item(row, 0).text()
        reply = QMessageBox.question(self, 'تأكيد الحذف', f'هل أنت متأكد من حذف الطالب {student_id}؟',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.student_controller.DeleteStudent(student_id)
            if success:
                QMessageBox.information(self, "نجح", message)
                self.LoadData()
            else:
                QMessageBox.warning(self, "خطأ", message)
    
    def CreateDoctorsTab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._CreateDoctorsListPanel(), 1)
        main_layout.addWidget(self._CreateDoctorsFormPanel(), 1)
        layout.addLayout(main_layout)
        return widget
    
    def _CreateDoctorsListPanel(self) -> QFrame:
        frame = self._CreateCardFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("قائمة الدكاترة"))
        self.doctors_table = QTableWidget()
        self.doctors_table.setColumnCount(4)
        self.doctors_table.setHorizontalHeaderLabels(['المعرف', 'الاسم', 'البريد', 'التخصصات'])
        self.doctors_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.doctors_table.itemSelectionChanged.connect(self.OnDoctorSelected)
        layout.addWidget(self.doctors_table)
        delete_button = QPushButton("حذف الدكتور المحدد")
        delete_button.setProperty("class", "danger")
        delete_button.clicked.connect(self.HandleDeleteDoctor)
        layout.addWidget(delete_button)
        return frame
    
    def _CreateDoctorsFormPanel(self) -> QFrame:
        frame = self._CreateCardFrame()
        layout = QVBoxLayout(frame)
        layout.addWidget(QLabel("إضافة/تحديث دكتور"))
        form_layout = QFormLayout()
        self.doctor_id_input = QLineEdit()
        self.doctor_id_input.setPlaceholderText("معرف الدكتور")
        self.doctor_name_input = QLineEdit()
        self.doctor_name_input.setPlaceholderText("اسم الدكتور")
        self.doctor_email_input = QLineEdit()
        self.doctor_email_input.setPlaceholderText("البريد الإلكتروني")
        self.doctor_courses_input = QLineEdit()
        self.doctor_courses_input.setPlaceholderText("المقررات المفضلة")
        self.doctor_availability_input = QLineEdit()
        self.doctor_availability_input.setPlaceholderText("أوقات التوفر")
        form_layout.addRow('معرف الدكتور:', self.doctor_id_input)
        form_layout.addRow('اسم الدكتور:', self.doctor_name_input)
        form_layout.addRow('البريد:', self.doctor_email_input)
        form_layout.addRow('المقررات:', self.doctor_courses_input)
        form_layout.addRow('التوفر:', self.doctor_availability_input)
        layout.addLayout(form_layout)
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("حفظ الدكتور")
        save_button.clicked.connect(self.HandleSaveDoctor)
        clear_button = QPushButton("مسح النموذج")
        clear_button.setProperty("class", "secondary")
        clear_button.clicked.connect(self.ClearDoctorForm)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(clear_button)
        layout.addLayout(buttons_layout)
        return frame
    
    def LoadDoctors(self):
        self.doctors_table.setRowCount(0)
        doctors = self.doctor_controller.GetAllDoctors()
        for i, doctor in enumerate(doctors):
            self.doctors_table.insertRow(i)
            self.doctors_table.setItem(i, 0, QTableWidgetItem(str(doctor[0])))
            self.doctors_table.setItem(i, 1, QTableWidgetItem(doctor[1]))
            self.doctors_table.setItem(i, 2, QTableWidgetItem(doctor[2]))
            self.doctors_table.setItem(i, 3, QTableWidgetItem(doctor[3] or ""))
    
    def OnDoctorSelected(self):
        row = self.doctors_table.currentRow()
        if row >= 0:
            doctor_id = self.doctors_table.item(row, 0).text()
            doctor = self.doctor_controller.GetDoctor(doctor_id)
            if doctor:
                self.doctor_id_input.setText(str(doctor[0]))
                self.doctor_name_input.setText(doctor[1])
                self.doctor_email_input.setText(doctor[2])
                self.doctor_courses_input.setText(doctor[3] or "")
                self.doctor_availability_input.setText(doctor[4] or "")
    
    def HandleSaveDoctor(self):
        doctor_id = self.doctor_id_input.text().strip()
        name = self.doctor_name_input.text().strip()
        email = self.doctor_email_input.text().strip()
        courses = self.doctor_courses_input.text().strip()
        availability = self.doctor_availability_input.text().strip()
        
        if not doctor_id or not name or not email:
            QMessageBox.warning(self, "خطأ", "الرجاء ملء جميع الحقول المطلوبة")
            return
        
        success, message = self.doctor_controller.AddDoctor(doctor_id, name, email, courses, availability)
        if success:
            QMessageBox.information(self, "نجح", message)
            self.ClearDoctorForm()
            self.LoadDoctors()
        else:
            QMessageBox.warning(self, "خطأ", message)
    
    def HandleDeleteDoctor(self):
        row = self.doctors_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "تحذير", "الرجاء اختيار دكتور أولاً")
            return
        
        doctor_id = self.doctors_table.item(row, 0).text()
        reply = QMessageBox.question(self, 'تأكيد الحذف', f'هل أنت متأكد من حذف الدكتور {doctor_id}؟',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.doctor_controller.DeleteDoctor(doctor_id)
            if success:
                QMessageBox.information(self, "نجح", message)
                self.LoadDoctors()
            else:
                QMessageBox.warning(self, "خطأ", message)
    
    def ClearDoctorForm(self):
        self.doctor_id_input.clear()
        self.doctor_name_input.clear()
        self.doctor_email_input.clear()
        self.doctor_courses_input.clear()
        self.doctor_availability_input.clear()
    
    def UpdateSectionsCombo(self, course_code: str):
        self.section_course_combo.clear()
        for course in self.course_controller.GetAllCourses():
            self.section_course_combo.addItem(course.course_code)