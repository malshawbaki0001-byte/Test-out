"""Doctor Module - لوحة تحكم الدكتور"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QFrame, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QStatusBar, QApplication, QComboBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush
from CONTROLLERS import CourseController, DoctorController
from DOMAIN_MODELS import DomainModels
from APP_MODULE import AppModule

class DoctorModule:
    """وحدة واجهة الدكتور"""

    class DashboardBase(QWidget):
        """الكلاس الأساسي لواجهة الدكتور"""
        def __init__(self):
            super().__init__()
            self.is_dark_mode = False

        def ToggleTheme(self):
            """تبديل بين الوضع الفاتح والداكن"""
            app = QApplication.instance()
            self.is_dark_mode = not self.is_dark_mode
            app.setStyleSheet(AppModule.DARK_MODE_QSS if self.is_dark_mode else AppModule.LIGHT_MODE_QSS)
            if hasattr(self, 'theme_button'):
                self.theme_button.setText("☀️" if self.is_dark_mode else "🌙")

        def HandleSignout(self):
            """معالجة تسجيل الخروج"""
            if QMessageBox.question(self, 'تسجيل الخروج', 'هل أنت متأكد من تسجيل الخروج؟',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.close()
                QApplication.instance().exit(100)

    class Dashboard(DashboardBase):
        """لوحة تحكم الدكتور الرئيسية"""

        def __init__(self, doctor: DomainModels.Doctor):
            super().__init__()
            self.doctor = doctor
            self.course_controller = CourseController()
            self.doctor_controller = DoctorController(self.course_controller)

            self.setWindowTitle(f'لوحة تحكم الدكتور - مرحباً د. {doctor.name}')
            self.setGeometry(100, 100, 1200, 700)
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

            self.InitUi()
            self.LoadData()

        def InitUi(self):
            """إعداد واجهة المستخدم"""
            layout = QVBoxLayout(self)

            # الشريط العلوي
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

            # بطاقة الترحيب والملخص
            welcome_card = self.CreateWelcomeCard()
            layout.addWidget(welcome_card)

            # التبويبات الرئيسية
            self.tab_widget = QTabWidget()
            self.tab_widget.addTab(self.CreateScheduleTab(), "📅 جدولي الأسبوعي")
            self.tab_widget.addTab(self.CreateCoursesTab(), "📚 مقرراتي")
            self.tab_widget.addTab(self.CreateAvailabilityTab(), "⏰ أوقات التوفر")
            self.tab_widget.addTab(self.CreateStatisticsTab(), "📊 الإحصائيات")
            self.tab_widget.addTab(self.CreateProfileTab(), "👤 ملفي الشخصي")

            layout.addWidget(self.tab_widget)

        def CreateWelcomeCard(self) -> QFrame:
            """إنشاء بطاقة الترحيب والملخص"""
            frame = QFrame()
            frame.setProperty("class", "card")
            AppModule.ApplyShadow(frame)

            layout = QVBoxLayout(frame)
            layout.setContentsMargins(20, 20, 20, 20)

            # عنوان الترحيب
            welcome_label = QLabel(f"مرحباً د. {self.doctor.name}")
            welcome_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            welcome_label.setObjectName("TitleLabel")
            layout.addWidget(welcome_label)

            # معلومات الدكتور
            info_label = QLabel(f"البريد الإلكتروني: {self.doctor.email}")
            info_label.setFont(QFont("Arial", 12))
            layout.addWidget(info_label)

            # ملخص سريع
            summary_layout = QHBoxLayout()

            # عدد المقررات
            self.courses_count_label = QLabel("عدد المقررات: 0")
            self.courses_count_label.setStyleSheet("font-weight: bold; color: #007bff;")
            summary_layout.addWidget(self.courses_count_label)

            # عدد الساعات
            self.hours_count_label = QLabel("عدد الساعات: 0")
            self.hours_count_label.setStyleSheet("font-weight: bold; color: #28a745;")
            summary_layout.addWidget(self.hours_count_label)

            # عدد الطلاب
            self.students_count_label = QLabel("عدد الطلاب: 0")
            self.students_count_label.setStyleSheet("font-weight: bold; color: #dc3545;")
            summary_layout.addWidget(self.students_count_label)

            summary_layout.addStretch()
            layout.addLayout(summary_layout)

            return frame

        def CreateScheduleTab(self) -> QWidget:
            """إنشاء تبويب الجدول الأسبوعي"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # عنوان
            title = QLabel("جدول المحاضرات الأسبوعي")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            layout.addWidget(title)

            # جدول الجدول الزمني الأسبوعي
            self.weekly_schedule_table = QTableWidget()
            self.weekly_schedule_table.setColumnCount(6)
            self.weekly_schedule_table.setRowCount(14)  # 8 صباحاً - 10 مساءً
            self.weekly_schedule_table.setHorizontalHeaderLabels(['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'السبت'])

            # أوقات الساعات
            time_labels = [f"{hour}:00 - {hour+1}:00" for hour in range(8, 22)]
            self.weekly_schedule_table.setVerticalHeaderLabels(time_labels)

            self.weekly_schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.weekly_schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.weekly_schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.weekly_schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)

            layout.addWidget(self.weekly_schedule_table)

            # زر التحديث
            refresh_button = QPushButton("🔄 تحديث الجدول")
            refresh_button.setProperty("class", "secondary")
            refresh_button.clicked.connect(self.LoadScheduleData)
            layout.addWidget(refresh_button)

            return widget

        def CreateCoursesTab(self) -> QWidget:
            """إنشاء تبويب المقررات المسندة"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # عنوان
            title = QLabel("المقررات المسندة لي")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            layout.addWidget(title)

            # جدول المقررات
            self.courses_table = QTableWidget()
            self.courses_table.setColumnCount(5)
            self.courses_table.setHorizontalHeaderLabels(['رمز المقرر', 'اسم المقرر', 'الشعبة', 'عدد الطلاب', 'الأوقات'])
            self.courses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            layout.addWidget(self.courses_table)

            # زر التحديث
            refresh_button = QPushButton("🔄 تحديث المقررات")
            refresh_button.setProperty("class", "secondary")
            refresh_button.clicked.connect(self.LoadCoursesData)
            layout.addWidget(refresh_button)

            return widget

        def CreateAvailabilityTab(self) -> QWidget:
            """إنشاء تبويب أوقات التوفر"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # عنوان
            title = QLabel("إدارة أوقات التوفر")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            layout.addWidget(title)

            # مجموعة أوقات التوفر
            availability_group = QGroupBox("أوقات التوفر الحالية")
            availability_layout = QVBoxLayout(availability_group)

            self.availability_text = QTextEdit()
            self.availability_text.setPlaceholderText("أدخل أوقات التوفر هنا...\nمثال: الأحد 8-10، الثلاثاء 2-4")
            self.availability_text.setMaximumHeight(100)
            availability_layout.addWidget(self.availability_text)

            # زر الحفظ
            save_button = QPushButton("💾 حفظ أوقات التوفر")
            save_button.clicked.connect(self.SaveAvailability)
            availability_layout.addWidget(save_button)

            layout.addWidget(availability_group)

            # مجموعة المقررات المفضلة
            preferences_group = QGroupBox("المقررات المفضلة")
            preferences_layout = QVBoxLayout(preferences_group)

            self.preferences_text = QTextEdit()
            self.preferences_text.setPlaceholderText("أدخل رموز المقررات المفضلة هنا...\nمثال: EE202, CS301, MATH101")
            self.preferences_text.setMaximumHeight(100)
            preferences_layout.addWidget(self.preferences_text)

            # زر الحفظ
            save_prefs_button = QPushButton("💾 حفظ المقررات المفضلة")
            save_prefs_button.clicked.connect(self.SavePreferences)
            preferences_layout.addWidget(save_prefs_button)

            layout.addWidget(preferences_group)

            return widget

        def CreateStatisticsTab(self) -> QWidget:
            """إنشاء تبويب الإحصائيات"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # عنوان
            title = QLabel("إحصائيات التدريس")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            layout.addWidget(title)

            # إحصائيات في بطاقات
            stats_layout = QVBoxLayout()

            # بطاقة الإحصائيات الأساسية
            basic_stats_group = QGroupBox("الإحصائيات الأساسية")
            basic_layout = QVBoxLayout(basic_stats_group)

            self.total_courses_stat = QLabel("إجمالي المقررات: 0")
            self.total_hours_stat = QLabel("إجمالي الساعات: 0")
            self.total_students_stat = QLabel("إجمالي الطلاب: 0")
            self.weekly_hours_stat = QLabel("ساعات الأسبوع: 0")

            basic_layout.addWidget(self.total_courses_stat)
            basic_layout.addWidget(self.total_hours_stat)
            basic_layout.addWidget(self.total_students_stat)
            basic_layout.addWidget(self.weekly_hours_stat)

            stats_layout.addWidget(basic_stats_group)

            # بطاقة التوزيع اليومي
            daily_group = QGroupBox("التوزيع اليومي للمحاضرات")
            daily_layout = QVBoxLayout(daily_group)

            self.daily_stats_text = QLabel("سيتم عرض إحصائيات التوزيع اليومي هنا")
            daily_layout.addWidget(self.daily_stats_text)

            stats_layout.addWidget(daily_group)

            layout.addLayout(stats_layout)

            # زر تحديث الإحصائيات
            refresh_stats_button = QPushButton("🔄 تحديث الإحصائيات")
            refresh_stats_button.setProperty("class", "secondary")
            refresh_stats_button.clicked.connect(self.LoadStatisticsData)
            layout.addWidget(refresh_stats_button)

            return widget

        def CreateProfileTab(self) -> QWidget:
            """إنشاء تبويب الملف الشخصي"""
            widget = QWidget()
            layout = QVBoxLayout(widget)

            # عنوان
            title = QLabel("بياناتي الشخصية")
            title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            layout.addWidget(title)

            # معلومات الدكتور
            profile_group = QGroupBox("المعلومات الشخصية")
            profile_layout = QVBoxLayout(profile_group)

            self.profile_name_label = QLabel(f"الاسم: {self.doctor.name}")
            self.profile_email_label = QLabel(f"البريد الإلكتروني: {self.doctor.email}")
            self.profile_id_label = QLabel(f"المعرف: {self.doctor.doctor_id}")

            profile_layout.addWidget(self.profile_name_label)
            profile_layout.addWidget(self.profile_email_label)
            profile_layout.addWidget(self.profile_id_label)

            layout.addWidget(profile_group)

            return widget

        def LoadData(self):
            """تحميل جميع البيانات"""
            self.LoadScheduleData()
            self.LoadCoursesData()
            self.LoadAvailabilityData()
            self.LoadStatisticsData()
            self.UpdateSummary()

        def LoadScheduleData(self):
            """تحميل بيانات الجدول الأسبوعي"""
            # مسح الجدول
            for row in range(self.weekly_schedule_table.rowCount()):
                for col in range(self.weekly_schedule_table.columnCount()):
                    self.weekly_schedule_table.setItem(row, col, None)

            # جلب الجدول الزمني للدكتور
            schedule = self.doctor_controller.get_schedule(self.doctor.doctor_id)

            # خريطة الأيام للأعمدة
            day_to_column = {
                'الأحد': 0, 'الإثنين': 1, 'الثلاثاء': 2,
                'الأربعاء': 3, 'الخميس': 4, 'السبت': 5
            }

            # ألوان للمقررات المختلفة
            colors = [
                QColor(173, 216, 230), QColor(144, 238, 144), QColor(255, 182, 193),
                QColor(221, 160, 221), QColor(255, 218, 185), QColor(176, 224, 230)
            ]
            course_colors = {}
            color_index = 0

            for item in schedule:
                course_code = item.get('course_code', '')
                start_time = item.get('start_time')
                days = item.get('days', '')

                if course_code not in course_colors:
                    course_colors[course_code] = colors[color_index % len(colors)]
                    color_index += 1

                color = course_colors[course_code]

                if start_time is not None and days:
                    start_hour = start_time // 60  # تحويل الدقائق إلى ساعات
                    end_hour = (start_time + (item.get('end_time', start_time) - start_time)) // 60

                    # التأكد من أن الأوقات في النطاق المسموح
                    start_row = max(0, start_hour - 8)  # 8 صباحاً هو الصف 0
                    end_row = min(14, end_hour - 8 + 1)  # 10 مساءً هو الصف الأخير

                    day_list = [day.strip() for day in days.split(',') if day.strip()]

                    for day_name in day_list:
                        if day_name in day_to_column:
                            day_column = day_to_column[day_name]

                            for row in range(start_row, end_row):
                                if 0 <= row < self.weekly_schedule_table.rowCount():
                                    course_info = f"{course_code}\n{item.get('course_name', '')}"
                                    table_item = QTableWidgetItem(course_info)
                                    table_item.setBackground(QBrush(color))
                                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                    self.weekly_schedule_table.setItem(row, day_column, table_item)

        def LoadCoursesData(self):
            """تحميل بيانات المقررات المسندة"""
            self.courses_table.setRowCount(0)

            # جلب تعيينات الدكتور
            assignments = self.doctor_controller.get_assignments(self.doctor.doctor_id)

            for i, assignment in enumerate(assignments):
                self.courses_table.insertRow(i)

                course_code = assignment[1]  # course_code
                section_id = assignment[2]   # section_id

                # جلب معلومات المقرر
                course = self.course_controller.get_course(course_code)
                course_name = course.name if course else "غير معروف"

                # جلب معلومات الشعبة
                section_info = ""
                students_count = 0
                schedule_info = ""

                if section_id:
                    section = self.course_controller.get_section(section_id)
                    if section:
                        section_info = section_id
                        students_count = section.current_enrollment
                        schedule_info = f"{section.start_time}:00 - {section.end_time}:00 ({section.days})"

                self.courses_table.setItem(i, 0, QTableWidgetItem(course_code))
                self.courses_table.setItem(i, 1, QTableWidgetItem(course_name))
                self.courses_table.setItem(i, 2, QTableWidgetItem(section_info))
                self.courses_table.setItem(i, 3, QTableWidgetItem(str(students_count)))
                self.courses_table.setItem(i, 4, QTableWidgetItem(schedule_info))

        def LoadAvailabilityData(self):
            """تحميل بيانات أوقات التوفر والمقررات المفضلة"""
            self.availability_text.setText(self.doctor.time_availability)
            self.preferences_text.setText(self.doctor.preferred_courses)

        def LoadStatisticsData(self):
            """تحميل بيانات الإحصائيات"""
            assignments = self.doctor_controller.get_assignments(self.doctor.doctor_id)

            total_courses = len(assignments)
            total_students = 0
            weekly_hours = 0

            # حساب إحصائيات التوزيع اليومي
            daily_count = {'الأحد': 0, 'الإثنين': 0, 'الثلاثاء': 0, 'الأربعاء': 0, 'الخميس': 0, 'السبت': 0}

            for assignment in assignments:
                section_id = assignment[2]
                if section_id:
                    section = self.course_controller.get_section(section_id)
                    if section:
                        total_students += section.current_enrollment

                        # حساب ساعات الأسبوع
                        if section.start_time and section.end_time:
                            hours = (section.end_time - section.start_time) // 60
                            weekly_hours += hours

                            # عد المحاضرات لكل يوم
                            if section.days:
                                days_list = [day.strip() for day in section.days.split(',') if day.strip()]
                                for day in days_list:
                                    if day in daily_count:
                                        daily_count[day] += 1

            # تحديث الإحصائيات
            self.total_courses_stat.setText(f"إجمالي المقررات: {total_courses}")
            self.total_hours_stat.setText(f"إجمالي الساعات: {weekly_hours}")
            self.total_students_stat.setText(f"إجمالي الطلاب: {total_students}")
            self.weekly_hours_stat.setText(f"ساعات الأسبوع: {weekly_hours}")

            # تحديث إحصائيات التوزيع اليومي
            daily_text = "التوزيع اليومي للمحاضرات:\n"
            for day, count in daily_count.items():
                daily_text += f"{day}: {count} محاضرات\n"
            self.daily_stats_text.setText(daily_text)

        def UpdateSummary(self):
            """تحديث الملخص في بطاقة الترحيب"""
            assignments = self.doctor_controller.get_assignments(self.doctor.doctor_id)

            total_students = 0
            weekly_hours = 0

            for assignment in assignments:
                section_id = assignment[2]
                if section_id:
                    section = self.course_controller.get_section(section_id)
                    if section:
                        total_students += section.current_enrollment
                        if section.start_time and section.end_time:
                            weekly_hours += (section.end_time - section.start_time) // 60

            self.courses_count_label.setText(f"عدد المقررات: {len(assignments)}")
            self.hours_count_label.setText(f"عدد الساعات: {weekly_hours}")
            self.students_count_label.setText(f"عدد الطلاب: {total_students}")

        def SaveAvailability(self):
            """حفظ أوقات التوفر"""
            new_availability = self.availability_text.toPlainText().strip()

            # هنا يمكن إضافة منطق تحديث قاعدة البيانات
            # لكن بما أن الكود الموجود لا يدعم تحديث البيانات، سنعرض رسالة فقط
            QMessageBox.information(self, "تم الحفظ",
                                  f"تم حفظ أوقات التوفر:\n{new_availability}")

        def SavePreferences(self):
            """حفظ المقررات المفضلة"""
            new_preferences = self.preferences_text.toPlainText().strip()

            # هنا يمكن إضافة منطق تحديث قاعدة البيانات
            # لكن بما أن الكود الموجود لا يدعم تحديث البيانات، سنعرض رسالة فقط
            QMessageBox.information(self, "تم الحفظ",
                                  f"تم حفظ المقررات المفضلة:\n{new_preferences}")

    # ============================================================================
    # نافذة تفاصيل المقرر
    # ============================================================================

    class CourseDetailsDialog(QDialog):
        """نافذة عرض تفاصيل المقرر"""

        def __init__(self, course_code: str, course_controller: Controllers.CourseController, parent=None):
            super().__init__(parent)
            self.course_code = course_code
            self.course_controller = course_controller

            self.setWindowTitle(f'تفاصيل المقرر - {course_code}')
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setGeometry(300, 300, 500, 400)

            self.init_ui()
            self.load_data()

        def init_ui(self):
            layout = QVBoxLayout(self)

            # معلومات المقرر
            self.course_info_label = QLabel()
            self.course_info_label.setFont(QFont("Arial", 12))
            layout.addWidget(self.course_info_label)

            # قائمة الشعب
            layout.addWidget(QLabel("الشعب المتاحة:"))
            self.sections_table = QTableWidget()
            self.sections_table.setColumnCount(4)
            self.sections_table.setHorizontalHeaderLabels(['معرف الشعبة', 'المدرس', 'الأوقات', 'عدد الطلاب'])
            self.sections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            layout.addWidget(self.sections_table)

            # زر الإغلاق
            close_button = QPushButton("إغلاق")
            close_button.clicked.connect(self.accept)
            layout.addWidget(close_button)

        def load_data(self):
            """تحميل بيانات المقرر"""
            course = self.course_controller.get_course(self.course_code)
            if course:
                info_text = f"""
                <b>رمز المقرر:</b> {course.course_code}<br>
                <b>اسم المقرر:</b> {course.name}<br>
                <b>الساعات المعتمدة:</b> {course.credits}<br>
                <b>ساعات المحاضرات:</b> {course.lecture_hours}<br>
                <b>ساعات المختبر:</b> {course.lab_hours}<br>
                <b>المستوى:</b> {course.level}
                """
                self.course_info_label.setText(info_text)

            # تحميل الشعب
            sections = self.course_controller.get_all_sections_for_course(self.course_code)
            self.sections_table.setRowCount(len(sections))

            for i, section in enumerate(sections):
                self.sections_table.setItem(i, 0, QTableWidgetItem(section.section_id))
                self.sections_table.setItem(i, 1, QTableWidgetItem(section.instructor))
                self.sections_table.setItem(i, 2, QTableWidgetItem(f"{section.start_time}:00 - {section.end_time}:00"))
                self.sections_table.setItem(i, 3, QTableWidgetItem(str(section.current_enrollment)))
