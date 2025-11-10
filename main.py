import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTableWidget, QTableWidgetItem,
                             QTabWidget, QMessageBox, QDialog, QFormLayout,
                             QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# استيراد الملفات الأخرى
try:
    from database import Database
    from models import UserManager, Student
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all files are in the same directory")


class LoginDialog(QDialog):
    def _init_(self, user_manager):
        super()._init_()
        self.user_manager = user_manager
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Course Registration System - Login')
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # العنوان
        title = QLabel('Course Registration System')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title)

        # نموذج تسجيل الدخول
        form_layout = QFormLayout()

        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Enter User ID")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter Password")

        form_layout.addRow('User ID:', self.user_id_input)
        form_layout.addRow('Password:', self.password_input)

        layout.addLayout(form_layout)

        # أزرار
        button_layout = QHBoxLayout()

        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")

        button_layout.addWidget(login_btn)
        layout.addLayout(button_layout)

        # بيانات الدخول الافتراضية
        info_label = QLabel('Default Login:\nAdmin: ADMIN001 / admin123')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 10px;")
        layout.addWidget(info_label)

        self.setLayout(layout)

    def login(self):
        user_id = self.user_id_input.text().strip()
        password = self.password_input.text().strip()

        if not user_id or not password:
            QMessageBox.warning(self, 'Error', 'Please fill all fields')
            return

        user = self.user_manager.authenticate(user_id, password)
        if user:
            self.current_user = user
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Invalid User ID or Password')


class StudentDashboard(QMainWindow):
    def _init_(self, user, db):
        super()._init_()
        self.user = user
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'Student Dashboard - {self.user["name"]}')
        self.setGeometry(100, 100, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # العنوان
        title = QLabel(f'Welcome {self.user["name"]}')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)

        # تبويبات
        tabs = QTabWidget()

        # تبويب التسجيل
        register_tab = self.create_register_tab()
        tabs.addTab(register_tab, "Course Registration")

        # تبويب الجدول الدراسي
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "My Schedule")

        layout.addWidget(tabs)
        central_widget.setLayout(layout)

    def create_register_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # قسم المقررات المتاحة
        available_group = QGroupBox("Available Courses for Registration")
        available_layout = QVBoxLayout()

        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(5)
        self.courses_table.setHorizontalHeaderLabels([
            'Course Code', 'Course Name', 'Credits', 'Schedule', 'Classroom'
        ])

        # جعل الجدول يملأ المساحة
        self.courses_table.horizontalHeader().setStretchLastSection(True)

        # تعبئة البيانات المبدئية
        self.load_sample_courses()

        available_layout.addWidget(self.courses_table)
        available_group.setLayout(available_layout)
        layout.addWidget(available_group)

        # أزرار التحكم
        button_layout = QHBoxLayout()

        register_btn = QPushButton('Register Selected Courses')
        register_btn.clicked.connect(self.register_courses)
        register_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 8px; }")

        refresh_btn = QPushButton('Refresh List')
        refresh_btn.clicked.connect(self.load_sample_courses)
        refresh_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; padding: 8px; }")

        button_layout.addWidget(register_btn)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def load_sample_courses(self):
        sample_courses = [
            ["COE100", "Programming Fundamentals", "3", "Mon-Wed 10:00-11:30", "Room 101"],
            ["COE200", "Data Structures", "3", "Tue-Thu 09:00-10:30", "Room 102"],
            ["COE210", "Digital Logic Design", "4", "Mon-Wed 13:00-14:30", "Lab A"],
            ["COE300", "Algorithms", "3", "Tue-Thu 11:00-12:30", "Room 103"],
            ["COE310", "Computer Architecture", "4", "Mon-Wed 15:00-16:30", "Lab B"],
        ]

        self.courses_table.setRowCount(len(sample_courses))
        for i, course in enumerate(sample_courses):
            for j, value in enumerate(course):
                item = QTableWidgetItem(str(value))
                self.courses_table.setItem(i, j, item)

        # ضبط أبعاد الأعمدة
        self.courses_table.resizeColumnsToContents()

    def register_courses(self):
        selected_items = self.courses_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'Warning', 'Please select at least one course')
            return

        selected_courses = set()
        for item in selected_items:
            row = item.row()
            course_code = self.courses_table.item(row, 0).text()
            selected_courses.add(course_code)

        if selected_courses:
            message = "Successfully registered for:\n" + "\n".join(selected_courses)
            QMessageBox.information(self, 'Success', message)
        else:
            QMessageBox.warning(self, 'Error', 'No courses selected')

    def create_schedule_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        info_label = QLabel('Your registered courses will appear here')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(QFont('Arial', 12))
        layout.addWidget(info_label)

        # عرض جدول مبسط
        schedule_text = QTextEdit()
        schedule_text.setPlainText("""Current Schedule:

COE100 - Programming Fundamentals
Time: Mon-Wed 10:00-11:30
Classroom: Room 101

COE200 - Data Structures  
Time: Tue-Thu 09:00-10:30
Classroom: Room 102

Total Credits: 6""")
        schedule_text.setReadOnly(True)
        layout.addWidget(schedule_text)

        widget.setLayout(layout)
        return widget


class AdminDashboard(QMainWindow):
    def _init_(self, user, db):
        super()._init_()
        self.user = user
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'Admin Dashboard - {self.user["name"]}')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        title = QLabel(f'Admin Dashboard - {self.user["name"]}')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)

        # إضافة محتوى لوحة الإدارة
        content_label = QLabel('''<center>
        <h3>Admin Functions:</h3>
        <p>• Manage Courses</p>
        <p>• Manage Students</p>
        <p>• View Registrations</p>
        <p>• System Settings</p>
        </center>''')
        content_label.setFont(QFont('Arial', 11))
        layout.addWidget(content_label)

        central_widget.setLayout(layout)


def main():
    # تهيئة التطبيق
    app = QApplication(sys.argv)

    # إنشاء إدارة المستخدمين وقاعدة البيانات
    db = Database()
    user_manager = UserManager(db)

    # عرض نافذة تسجيل الدخول
    login_dialog = LoginDialog(user_manager)

    if login_dialog.exec_() == QDialog.Accepted:
        current_user = login_dialog.current_user

        # عرض لوحة التحكم المناسبة
        if current_user['role'] == 'student':
            dashboard = StudentDashboard(current_user, db)
        else:
            dashboard = AdminDashboard(current_user, db)

        dashboard.show()
        sys.exit(app.exec_())
    else:
        print("Login cancelled")
        sys.exit()


if __name__ == "__main__":
    main()