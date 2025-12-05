"""Student Module - لوحة تحكم الطالب"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QFrame, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QStatusBar, QApplication, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
from CONTROLLERS import CourseController, StudentController
from DOMAIN_MODELS import DomainModels
from APP_MODULE import AppModule


class DashboardBase(QWidget):
        def __init__(self):
            super().__init__()
            self.is_dark_mode = False
        
        def ToggleTheme(self):
            app = QApplication.instance()
            self.is_dark_mode = not self.is_dark_mode
            app.setStyleSheet(AppModule.DARK_MODE_QSS if self.is_dark_mode else AppModule.LIGHT_MODE_QSS)
            if hasattr(self, 'theme_button'):
                self.theme_button.setText("☀️" if self.is_dark_mode else "🌙")
        
        def HandleSignout(self):
            if QMessageBox.question(self, 'تسجيل الخروج', 'هل أنت متأكد؟',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.close()
                QApplication.instance().exit(100)
    
class Dashboard(DashboardBase):
        def __init__(self, student: DomainModels.Student):
            super().__init__()
            self.student = student
            self.registered_course_credits = []
            self.course_controller = Controllers.CourseController()
            self.student_controller = Controllers.StudentController(self.course_controller)
            self.setWindowTitle(f'نظام التسجيل - مرحباً {student.name}')
            self.setGeometry(100, 100, 1200, 700)
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
            self.hours_warning_label = QLabel("")
            self.hours_warning_label.setWordWrap(True)
            self.hours_warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hours_warning_label.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; padding: 10px; border-radius: 5px; margin: 5px;")
            self.hours_warning_label.setVisible(False)
            layout.addWidget(self.hours_warning_label)
            main_layout = QHBoxLayout()
            main_layout.addWidget(self.CreateAvailableCoursesPanel(), 1)
            main_layout.addWidget(self.CreateSectionsPanel(), 2)
            main_layout.addWidget(self.CreateSchedulePanel(), 2)
            layout.addLayout(main_layout)
        
        def CreateAvailableCoursesPanel(self) -> QFrame:
            frame = self._CreateCardFrame()
            layout = QVBoxLayout(frame)
            layout.addWidget(QLabel(f"الطالب: {self.student.name}\nالبرنامج: {self.student.program} - المستوى {self.student.level}"))
            self.level_combo = QComboBox()
            self.level_combo.addItems([str(i) for i in range(1, 11)])
            self.level_combo.setCurrentText(str(self.student.level))
            self.level_combo.currentTextChanged.connect(self.OnLevelChanged)
            layout.addWidget(QLabel('المستوى:'))
            layout.addWidget(self.level_combo)
            layout.addWidget(QLabel('الخطوة 1: اختر مادة'))
            self.courses_list = QListWidget()
            self.courses_list.currentItemChanged.connect(self.OnCourseSelected)
            layout.addWidget(self.courses_list)
            refresh_button = QPushButton('🔄 تحديث قائمة المقررات')
            refresh_button.setProperty("class", "secondary")
            refresh_button.clicked.connect(self.LoadData)
            layout.addWidget(refresh_button)
            return frame
        
        def CreateSectionsPanel(self) -> QFrame:
            frame = self._CreateCardFrame()
            layout = QVBoxLayout(frame)
            layout.addWidget(QLabel('الخطوة 2: اختر شعبة'))
            self.sections_table = QTableWidget()
            self.sections_table.setColumnCount(6)
            self.sections_table.setHorizontalHeaderLabels(['المدرس', 'الوقت', 'القاعة', 'السعة', 'المسجلين', 'ID'])
            self.sections_table.setColumnHidden(5, True)
            layout.addWidget(self.sections_table)
            self.add_button = QPushButton('إضافة الشعبة المحددة')
            self.add_button.clicked.connect(self.HandleAddSection)
            layout.addWidget(self.add_button)
            return frame
        
        def CreateSchedulePanel(self) -> QFrame:
            frame = self._CreateCardFrame()
            layout = QVBoxLayout(frame)
            layout.addWidget(QLabel('جدولي الحالي'))
            schedule_tabs = QTabWidget()
            list_tab = QWidget()
            list_layout = QVBoxLayout(list_tab)
            self.schedule_table = QTableWidget()
            self.schedule_table.setColumnCount(6)
            self.schedule_table.setHorizontalHeaderLabels(['المادة', 'المدرس', 'الجدول الزمني', 'القاعة', 'الساعات', 'ID'])
            self.schedule_table.setColumnHidden(5, True)
            self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            list_layout.addWidget(self.schedule_table)
            schedule_tabs.addTab(list_tab, "القائمة")
            timetable_tab = QWidget()
            timetable_layout = QVBoxLayout(timetable_tab)
            self.weekly_timetable = QTableWidget()
            self.weekly_timetable.setColumnCount(6)
            self.weekly_timetable.setRowCount(14)
            self.weekly_timetable.setHorizontalHeaderLabels(['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'السبت'])
            time_labels = [f"{hour}:00 - {hour+1}:00" for hour in range(8, 22)]
            self.weekly_timetable.setVerticalHeaderLabels(time_labels)
            self.weekly_timetable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.weekly_timetable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.weekly_timetable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.weekly_timetable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
            timetable_layout.addWidget(QLabel('الجدول الأسبوعي'))
            timetable_layout.addWidget(self.weekly_timetable)
            schedule_tabs.addTab(timetable_tab, "الجدول الأسبوعي")
            layout.addWidget(schedule_tabs)
            hours_layout = QHBoxLayout()
            self.passed_hours_label = QLabel("الساعات المجتازة: 0")
            self.registered_hours_label = QLabel("الساعات المسجلة: 0")
            self.total_hours_label = QLabel("الإجمالي: 0")
            hours_layout.addWidget(self.passed_hours_label)
            hours_layout.addWidget(self.registered_hours_label)
            hours_layout.addWidget(self.total_hours_label)
            layout.addLayout(hours_layout)
            self.validation_label = QLabel("")
            self.validation_label.setWordWrap(True)
            self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
            layout.addWidget(self.validation_label)
            buttons_layout = QHBoxLayout()
            self.remove_button = QPushButton('حذف الشعبة المحددة')
            self.remove_button.setProperty("class", "danger")
            self.remove_button.clicked.connect(self.HandleRemoveSection)
            self.transcript_button = QPushButton('عرض السجل الأكاديمي')
            self.transcript_button.setProperty("class", "secondary")
            self.transcript_button.clicked.connect(self.ShowTranscript)
            buttons_layout.addWidget(self.remove_button)
            buttons_layout.addWidget(self.transcript_button)
            layout.addLayout(buttons_layout)
            self.status_bar = QStatusBar()
            layout.addWidget(self.status_bar)
            return frame
        
        def _CreateCardFrame(self) -> QFrame:
            frame = QFrame()
            frame.setProperty("class", "card")
            AppModule.ApplyShadow(frame)
            return frame
        
        def LoadData(self):
            self.course_controller.RefreshCache()
            self.LoadAvailableCourses()
            self.LoadRegisteredSchedule()
            self.UpdateHoursDisplay()
        
        def OnLevelChanged(self, level_text: str):
            if level_text:
                self.LoadAvailableCoursesForLevel(int(level_text))
        
        def LoadAvailableCourses(self):
            level_text = self.level_combo.currentText()
            if level_text:
                self.LoadAvailableCoursesForLevel(int(level_text))
        
        def LoadAvailableCoursesForLevel(self, level: int):
            self.courses_list.clear()
            for course in self.course_controller.GetAvailableCourses(self.student.program, level):
                item = QListWidgetItem(f"{course.course_code} - {course.name}")
                item.setData(Qt.ItemDataRole.UserRole, course.course_code)
                self.courses_list.addItem(item)
        
        def LoadRegisteredSchedule(self):
            self.schedule_table.setRowCount(0)
            self.registered_course_credits = []
            for i, registration in enumerate(self.student.schedule):
                section_id = registration.get('id')
                section = self.course_controller.GetSection(section_id)
                if not section:
                    continue
                course = self.course_controller.GetCourse(section.course_code)
                if not course:
                    continue
                self.registered_course_credits.append(course.credits)
                self.schedule_table.insertRow(i)
                self.schedule_table.setItem(i, 0, QTableWidgetItem(course.course_code))
                self.schedule_table.setItem(i, 1, QTableWidgetItem(section.instructor))
                # عرض معلومات الجدول الزمني
                schedule_info = section.GetLectureTimeString()
                if section.lab_schedule:
                    schedule_info += f"\nمختبر: {section.GetLabTimeString()}"
                self.schedule_table.setItem(i, 2, QTableWidgetItem(schedule_info))
                self.schedule_table.setItem(i, 3, QTableWidgetItem(section.lecture_schedule.hall if section.lecture_schedule else ""))
                self.schedule_table.setItem(i, 4, QTableWidgetItem(str(course.credits)))
                self.schedule_table.setItem(i, 5, QTableWidgetItem(section_id))
            self.UpdateWeeklyTimetable()
        
        def UpdateWeeklyTimetable(self):
            for row in range(self.weekly_timetable.rowCount()):
                for col in range(self.weekly_timetable.columnCount()):
                    self.weekly_timetable.setItem(row, col, None)
            colors = [QColor(173, 216, 230), QColor(144, 238, 144), QColor(255, 182, 193),
                      QColor(221, 160, 221), QColor(255, 218, 185), QColor(176, 224, 230), QColor(255, 228, 196)]
            course_colors = {}
            color_index = 0
            for registration in self.student.schedule:
                section_id = registration.get('id')
                section = self.course_controller.GetSection(section_id)
                if not section:
                    continue
                course = self.course_controller.GetCourse(section.course_code)
                if not course:
                    continue
                if course.course_code not in course_colors:
                    course_colors[course.course_code] = colors[color_index % len(colors)]
                    color_index += 1
                color = course_colors[course.course_code]

                # إضافة المحاضرة إلى الجدول الأسبوعي
                if section.lecture_schedule:
                    self._AddScheduleToTimetable(section.lecture_schedule, course.course_code,
                                               section.instructor, color, "محاضرة")

                # إضافة المختبر إلى الجدول الأسبوعي
                if section.lab_schedule:
                    self._AddScheduleToTimetable(section.lab_schedule, course.course_code,
                                               section.instructor, color, "مختبر")

    def _AddScheduleToTimetable(self, schedule: 'DomainModels.SectionSchedule', course_code: str,
                               instructor: str, color: QColor, schedule_type: str):
        """إضافة جدول زمني إلى الجدول الأسبوعي"""
        start_row, end_row = schedule.start_time - 8, schedule.end_time - 8
        days_str = schedule.days or ''
        hall = schedule.hall or ''

        if days_str:
            day_to_column = {'الأحد': 0, 'الإثنين': 1, 'الثلاثاء': 2, 'الأربعاء': 3, 'الخميس': 4, 'السبت': 5}
            days_list = [day.strip() for day in days_str.split(',') if day.strip()]
            for day_name in days_list:
                if day_name in day_to_column:
                    day_column = day_to_column[day_name]
                    for row in range(start_row, end_row):
                        if 0 <= row < self.weekly_timetable.rowCount():
                            item = QTableWidgetItem(f"{course_code}\n{instructor}\n{hall}\n({schedule_type})")
                            item.setBackground(QBrush(color))
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.weekly_timetable.setItem(row, day_column, item)
        else:
            for row in range(start_row, end_row):
                if 0 <= row < self.weekly_timetable.rowCount():
                    item = QTableWidgetItem(f"{course_code}\n{instructor}\n{hall}\n({schedule_type})")
                    item.setBackground(QBrush(color))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.weekly_timetable.setItem(row, 0, item)
        
        def UpdateHoursDisplay(self):
            passed = self.student.GetCompletedCredits(self.course_controller._course_cache)
            registered = sum(self.registered_course_credits)
            total = passed + registered
            self.passed_hours_label.setText(f"الساعات المجتازة: {passed}")
            self.registered_hours_label.setText(f"الساعات المسجلة: {registered}")
            self.total_hours_label.setText(f"الإجمالي: {total}")
            is_valid, message = DomainModels.RegistrationValidator.ValidateCreditHours(registered)
            if not is_valid:
                self.hours_warning_label.setText(f"⚠️ تحذير: {message}")
                self.hours_warning_label.setVisible(True)
            else:
                self.hours_warning_label.setVisible(False)
        
        def OnCourseSelected(self, current, previous):
            if not current:
                return
            course_code = current.data(Qt.ItemDataRole.UserRole)
            sections = [s for s in self.course_controller._section_cache.values() if s.course_code == course_code]
            self.sections_table.setRowCount(0)
            for i, section in enumerate(sections):
                self.sections_table.insertRow(i)
                self.sections_table.setItem(i, 0, QTableWidgetItem(section.instructor))
                self.sections_table.setItem(i, 1, QTableWidgetItem(f"{section.start_time}:00 - {section.end_time}:00"))
                self.sections_table.setItem(i, 2, QTableWidgetItem(section.hall))
                self.sections_table.setItem(i, 3, QTableWidgetItem(str(section.max_capacity)))
                self.sections_table.setItem(i, 4, QTableWidgetItem(str(section.current_enrollment)))
                self.sections_table.setItem(i, 5, QTableWidgetItem(section.section_id))
        
        def HandleAddSection(self):
            row = self.sections_table.currentRow()
            if row == -1:
                self.validation_label.setText("⚠️ الرجاء اختيار شعبة أولاً")
                self.validation_label.setStyleSheet("color: #ffc107; font-weight: bold; padding: 5px;")
                return
            section_id = self.sections_table.item(row, 5).text()
            success, message = self.student_controller.RegisterStudent(self.student, section_id)
            if success:
                self.status_bar.showMessage(message, 3000)
                self.validation_label.setText("✅ تم التسجيل بنجاح")
                self.validation_label.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px;")
                self.LoadData()
            else:
                self.validation_label.setText(f"❌ {message}")
                self.validation_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 5px;")
                QMessageBox.warning(self, 'خطأ', message)
        
        def HandleRemoveSection(self):
            row = self.schedule_table.currentRow()
            if row == -1:
                QMessageBox.warning(self, 'تحذير', 'الرجاء اختيار شعبة أولاً')
                return
            section_id = self.schedule_table.item(row, 5).text()
            success, message = self.student_controller.UnregisterStudent(self.student, section_id)
            if success:
                self.status_bar.showMessage(message, 3000)
                self.validation_label.setText("")
                self.LoadData()
            else:
                QMessageBox.warning(self, 'خطأ', message)
        
        def ShowTranscript(self):
            dialog = TranscriptDialog(self.student, self.course_controller, self)
            dialog.exec()
    
    class TranscriptDialog(QDialog):
        def __init__(self, student: DomainModels.Student, course_controller: Controllers.CourseController, parent=None):
            super().__init__(parent)
            self.student = student
            self.course_controller = course_controller
            self.setWindowTitle(f'السجل الأكاديمي - {student.name}')
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setGeometry(200, 200, 600, 400)
            layout = QVBoxLayout(self)
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(['رمز المادة', 'اسم المادة', 'الساعات'])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            total_hours = 0
            for i, course_code in enumerate(student.transcript):
                course = course_controller.GetCourse(course_code)
                if course:
                    table.insertRow(i)
                    table.setItem(i, 0, QTableWidgetItem(course.course_code))
                    table.setItem(i, 1, QTableWidgetItem(course.name))
                    table.setItem(i, 2, QTableWidgetItem(str(course.credits)))
                    total_hours += course.credits
            layout.addWidget(table)
            total_label = QLabel(f"إجمالي الساعات المجتازة: {total_hours}")
            total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(total_label)