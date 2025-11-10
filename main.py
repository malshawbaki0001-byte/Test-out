import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QTabWidget, QMessageBox, QDialog, QFormLayout, QGroupBox, 
                             QTextEdit, QHeaderView, QComboBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from database import Database
from models import UserManager, Student, RegistrationSystem

class LoginDialog(QDialog):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('نظام تسجيل المقررات - تسجيل الدخول')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel('نظام تسجيل المقررات الدراسية')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title)
        
        # نموذج تسجيل الدخول
        form_layout = QFormLayout()
        
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("أدخل رقم المستخدم")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow('رقم المستخدم:', self.user_id_input)
        form_layout.addRow('كلمة المرور:', self.password_input)
        
        layout.addLayout(form_layout)
        
        # أزرار
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton('تسجيل الدخول')
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        
        button_layout.addWidget(login_btn)
        layout.addLayout(button_layout)
        
        # بيانات الدخول الافتراضية
        info_label = QLabel('''بيانات الدخول الافتراضية:
        المسؤول: ADMIN001 / admin123
        الطالب: STU001 / student123''')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666; font-size: 10px; margin-top: 10px;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def login(self):
        user_id = self.user_id_input.text().strip()
        password = self.password_input.text().strip()
        
        if not user_id or not password:
            QMessageBox.warning(self, 'خطأ', 'يرجى ملء جميع الحقول')
            return
        
        user = self.user_manager.authenticate(user_id, password)
        if user:
            self.current_user = user
            self.accept()
        else:
            QMessageBox.warning(self, 'خطأ', 'رقم المستخدم أو كلمة المرور غير صحيحة')

class StudentDashboard(QMainWindow):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.reg_system = RegistrationSystem(db)
        self.student = self.user_manager.get_student_profile(user['user_id'])
        self.semester = "2024-Fall"  # الفصل الحالي
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'لوحة الطالب - {self.user["name"]}')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel(f'مرحباً {self.user["name"]} - {self.student.program} - المستوى {self.student.current_level}')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)
        
        # تبويبات
        tabs = QTabWidget()
        
        # تبويب التسجيل
        register_tab = self.create_register_tab()
        tabs.addTab(register_tab, "تسجيل المقررات")
        
        # تبويب الجدول الدراسي
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "جدولي الدراسي")
        
        # تبويب السجل الدراسي
        transcript_tab = self.create_transcript_tab()
        tabs.addTab(transcript_tab, "سجلي الدراسي")
        
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
    
    def create_register_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # قسم المقررات المتاحة
        available_group = QGroupBox("المقررات المتاحة للتسجيل")
        available_layout = QVBoxLayout()
        
        self.available_courses_table = QTableWidget()
        self.available_courses_table.setColumnCount(7)
        self.available_courses_table.setHorizontalHeaderLabels([
            'كود المقرر', 'اسم المقرر', 'الساعات', 'الجدول', 'القاعة', 'السعة', 'الحالة'
        ])
        
        self.load_available_courses()
        
        available_layout.addWidget(self.available_courses_table)
        available_group.setLayout(available_layout)
        layout.addWidget(available_group)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton('تسجيل المقرر المحدد')
        register_btn.clicked.connect(self.register_selected_course)
        register_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")
        
        refresh_btn = QPushButton('تحديث القائمة')
        refresh_btn.clicked.connect(self.load_available_courses)
        refresh_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px; }")
        
        button_layout.addWidget(register_btn)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        # منطقة النتائج
        self.registration_result = QTextEdit()
        self.registration_result.setReadOnly(True)
        self.registration_result.setMaximumHeight(150)
        layout.addWidget(self.registration_result)
        
        widget.setLayout(layout)
        return widget
    
    def load_available_courses(self):
        available_courses = self.student.get_available_courses(self.db, self.semester)
        
        self.available_courses_table.setRowCount(len(available_courses))
        for i, course in enumerate(available_courses):
            self.available_courses_table.setItem(i, 0, QTableWidgetItem(course.course_code))
            self.available_courses_table.setItem(i, 1, QTableWidgetItem(course.name))
            self.available_courses_table.setItem(i, 2, QTableWidgetItem(str(course.credits)))
            self.available_courses_table.setItem(i, 3, QTableWidgetItem(course.schedule_info))
            self.available_courses_table.setItem(i, 4, QTableWidgetItem(course.classroom))
            
            current_enrollment = course.get_current_enrollment(self.db, self.semester)
            capacity_info = f"{current_enrollment}/{course.max_capacity}"
            self.available_courses_table.setItem(i, 5, QTableWidgetItem(capacity_info))
            
            # تحديد حالة المقرر
            if course.is_full(self.db, self.semester):
                status = "ممتلئ"
            elif not course.check_prerequisites(self.db, self.student.student_id):
                status = "متطلبات غير مكتملة"
            else:
                status = "متاح"
            
            self.available_courses_table.setItem(i, 6, QTableWidgetItem(status))
        
        self.available_courses_table.resizeColumnsToContents()
    
    def register_selected_course(self):
        selected_row = self.available_courses_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'تحذير', 'يرجى اختيار مقرر من القائمة')
            return
        
        course_code = self.available_courses_table.item(selected_row, 0).text()
        
        success, messages = self.reg_system.register_course(self.student, course_code, self.semester)
        
        result_text = "\n".join(messages)
        self.registration_result.setText(result_text)
        
        if success:
            QMessageBox.information(self, 'نجاح', 'تم التسجيل في المقرر بنجاح')
            self.load_available_courses()
    
    def create_schedule_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # جدول المقررات المسجلة
        schedule_group = QGroupBox("المقررات المسجلة في الفصل الحالي")
        schedule_layout = QVBoxLayout()
        
        self.registered_courses_table = QTableWidget()
        self.registered_courses_table.setColumnCount(6)
        self.registered_courses_table.setHorizontalHeaderLabels([
            'كود المقرر', 'اسم المقرر', 'الساعات', 'الجدول', 'القاعة', 'الإجراءات'
        ])
        
        self.load_registered_courses()
        
        schedule_layout.addWidget(self.registered_courses_table)
        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)
        
        # إجمالي الساعات
        self.credits_label = QLabel()
        self.update_credits_label()
        layout.addWidget(self.credits_label)
        
        widget.setLayout(layout)
        return widget
    
    def load_registered_courses(self):
        registered_courses = self.student.get_current_schedule(self.db, self.semester)
        
        self.registered_courses_table.setRowCount(len(registered_courses))
        for i, course in enumerate(registered_courses):
            self.registered_courses_table.setItem(i, 0, QTableWidgetItem(course.course_code))
            self.registered_courses_table.setItem(i, 1, QTableWidgetItem(course.name))
            self.registered_courses_table.setItem(i, 2, QTableWidgetItem(str(course.credits)))
            self.registered_courses_table.setItem(i, 3, QTableWidgetItem(course.schedule_info))
            self.registered_courses_table.setItem(i, 4, QTableWidgetItem(course.classroom))
            
            # زر حذف المقرر
            drop_button = QPushButton('حذف')
            drop_button.clicked.connect(lambda checked, row=i: self.drop_course(row))
            drop_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
            
            # إضافة الزر إلى الخلية
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(drop_button)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            self.registered_courses_table.setCellWidget(i, 5, cell_widget)
        
        self.registered_courses_table.resizeColumnsToContents()
        self.update_credits_label()
    
    def drop_course(self, row):
        course_code = self.registered_courses_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, 'تأكيد الحذف', 
                                   f'هل أنت متأكد من حذف المقرر {course_code}؟',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, message = self.reg_system.drop_course(self.student, course_code, self.semester)
            if success:
                QMessageBox.information(self, 'نجاح', message)
                self.load_registered_courses()
                self.load_available_courses()
            else:
                QMessageBox.warning(self, 'خطأ', message)
    
    def update_credits_label(self):
        registered_courses = self.student.get_current_schedule(self.db, self.semester)
        total_credits = sum(course.credits for course in registered_courses)
        self.credits_label.setText(f'إجمالي الساعات المعتمدة: {total_credits} / 18')
    
    def create_transcript_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # جدول السجل الدراسي
        transcript_group = QGroupBox("السجل الدراسي")
        transcript_layout = QVBoxLayout()
        
        self.transcript_table = QTableWidget()
        self.transcript_table.setColumnCount(4)
        self.transcript_table.setHorizontalHeaderLabels([
            'كود المقرر', 'اسم المقرر', 'الدرجة', 'الفصل'
        ])
        
        self.load_transcript()
        
        transcript_layout.addWidget(self.transcript_table)
        transcript_group.setLayout(transcript_layout)
        layout.addWidget(transcript_group)
        
        # إجمالي الساعات المكتملة
        self.completed_credits_label = QLabel()
        self.update_completed_credits_label()
        layout.addWidget(self.completed_credits_label)
        
        widget.setLayout(layout)
        return widget
    
    def load_transcript(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.course_code, c.name, t.grade, t.semester 
            FROM transcripts t
            JOIN courses c ON t.course_code = c.course_code
            WHERE t.student_id = ?
            ORDER BY t.semester
        ''', (self.student.student_id,))
        
        transcript = cursor.fetchall()
        conn.close()
        
        self.transcript_table.setRowCount(len(transcript))
        for i, record in enumerate(transcript):
            for j, value in enumerate(record):
                self.transcript_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        self.transcript_table.resizeColumnsToContents()
    
    def update_completed_credits_label(self):
        completed_credits = self.student.get_completed_credits(self.db)
        self.completed_credits_label.setText(f'إجمالي الساعات المكتملة: {completed_credits}')

class AdminDashboard(QMainWindow):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'لوحة الإدارة - {self.user["name"]}')
        self.setGeometry(100, 100, 1000, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        title = QLabel(f'لوحة إدارة النظام - {self.user["name"]}')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)
        
        # تبويبات الإدارة
        tabs = QTabWidget()
        
        # تبويب إدارة المقررات
        courses_tab = self.create_courses_tab()
        tabs.addTab(courses_tab, "إدارة المقررات")
        
        # تبويب إدارة الطلاب
        students_tab = self.create_students_tab()
        tabs.addTab(students_tab, "إدارة الطلاب")
        
        # تبويب التقارير
        reports_tab = self.create_reports_tab()
        tabs.addTab(reports_tab, "التقارير")
        
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
    
    def create_courses_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # جدول المقررات
        courses_table = QTableWidget()
        courses_table.setColumnCount(6)
        courses_table.setHorizontalHeaderLabels([
            'كود المقرر', 'اسم المقرر', 'الساعات', 'السعة', 'الجدول', 'القاعة'
        ])
        
        # تحميل بيانات المقررات
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
        conn.close()
        
        courses_table.setRowCount(len(courses))
        for i, course in enumerate(courses):
            for j in range(6):
                courses_table.setItem(i, j, QTableWidgetItem(str(course[j])))
        
        courses_table.resizeColumnsToContents()
        layout.addWidget(courses_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_students_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # جدول الطلاب
        students_table = QTableWidget()
        students_table.setColumnCount(5)
        students_table.setHorizontalHeaderLabels([
            'رقم الطالب', 'الاسم', 'البريد', 'التخصص', 'المستوى'
        ])
        
        # تحميل بيانات الطلاب
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.user_id, u.name, u.email, s.program, s.current_level
            FROM users u
            JOIN students s ON u.user_id = s.student_id
        ''')
        students = cursor.fetchall()
        conn.close()
        
        students_table.setRowCount(len(students))
        for i, student in enumerate(students):
            for j in range(5):
                students_table.setItem(i, j, QTableWidgetItem(str(student[j])))
        
        students_table.resizeColumnsToContents()
        layout.addWidget(students_table)
        
        widget.setLayout(layout)
        return widget
    
    def create_reports_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        reports_text = QTextEdit()
        reports_text.setPlainText('''تقارير النظام:

إحصائيات التسجيل:
- إجمالي الطلاب: 3
- إجمالي المقررات: 7
- متوسط الساعات المسجلة: 12

المقررات الأكثر طلباً:
1. COE100 - Programming Fundamentals
2. COE200 - Data Structures
3. COE300 - Algorithms

التخصصات:
- Computer: 1 طالب
- Communications: 1 طالب  
- Power: 1 طالب''')
        reports_text.setReadOnly(True)
        layout.addWidget(reports_text)
        
        widget.setLayout(layout)
        return widget

def main():
    app = QApplication(sys.argv)
    
    # تهيئة النظام
    db = Database()
    user_manager = UserManager(db)
    
    # عرض نافذة تسجيل الدخول
    login_dialog = LoginDialog(user_manager)
    
    if login_dialog.exec_() == QDialog.Accepted:
        current_user = login_dialog.current_user
        
        # عرض لوحة التحكم المناسبة
        if current_user['role'] == 'student':
            # الحصول على بيانات الطالب الكاملة
            student_profile = user_manager.get_student_profile(current_user['user_id'])
            if student_profile:
                dashboard = StudentDashboard(current_user, db)
                dashboard.show()
            else:
                QMessageBox.critical(None, 'خطأ', 'لم يتم العثور على بيانات الطالب')
                sys.exit(1)
        else:
            dashboard = AdminDashboard(current_user, db)
            dashboard.show()
        
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__ == "__main__":
    main()
