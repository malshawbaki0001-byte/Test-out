import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QComboBox, QTableWidget, QTableWidgetItem, 
                             QTabWidget, QMessageBox, QDialog, QFormLayout,
                             QGroupBox, QListWidget, QTextEdit, QHeaderView,
                             QSpinBox, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from database import Database
from models import UserManager, Student

class LoginDialog(QDialog):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.current_user = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('نظام تسجيل المقررات - تسجيل الدخول')
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel('نظام تسجيل المقررات الدراسية')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(title)
        
        # نموذج تسجيل الدخول
        form_layout = QFormLayout()
        
        self.user_id_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow('رقم المستخدم:', self.user_id_input)
        form_layout.addRow('كلمة المرور:', self.password_input)
        
        layout.addLayout(form_layout)
        
        # أزرار
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton('تسجيل الدخول')
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        button_layout.addWidget(login_btn)
        
        layout.addLayout(button_layout)
        
        # بيانات الدخول الافتراضية
        info_label = QLabel('بيانات الدخول:\nالمسؤول: ADMIN001 / admin123')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def login(self):
        user_id = self.user_id_input.text()
        password = self.password_input.text()
        
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
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'لوحة الطالب - {self.user["name"]}')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel(f'مرحباً {self.user["name"]}')
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
        
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
    
    def create_register_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # قسم المقررات المتاحة
        available_group = QGroupBox("المقررات المتاحة للتسجيل")
        available_layout = QVBoxLayout()
        
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(5)
        self.courses_table.setHorizontalHeaderLabels([
            'كود المقرر', 'اسم المقرر', 'الساعات', 'الجدول', 'القاعة'
        ])
        
        # تعبئة البيانات المبدئية
        self.load_sample_courses()
        
        available_layout.addWidget(self.courses_table)
        available_group.setLayout(available_layout)
        layout.addWidget(available_group)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        register_btn = QPushButton('تسجيل المقررات المحددة')
        register_btn.clicked.connect(self.register_courses)
        register_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; }")
        
        button_layout.addWidget(register_btn)
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def load_sample_courses(self):
        sample_courses = [
            ["COE100", "Programming Fundamentals", "3", "Mon-Wed 10:00-11:30", "Room 101"],
            ["COE200", "Data Structures", "3", "Tue-Thu 09:00-10:30", "Room 102"],
            ["COE210", "Digital Logic Design", "4", "Mon-Wed 13:00-14:30", "Lab A"],
            ["COE300", "Algorithms", "3", "Tue-Thu 11:00-12:30", "Room 103"],
        ]
        
        self.courses_table.setRowCount(len(sample_courses))
        for i, course in enumerate(sample_courses):
            for j, value in enumerate(course):
                self.courses_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def register_courses(self):
        selected_items = self.courses_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'تحذير', 'لم تقم باختيار أي مقرر')
            return
        
        selected_courses = []
        for item in selected_items:
            if item.column() == 0:  # كود المقرر
                selected_courses.append(item.text())
        
        message = "تم تسجيل المقررات التالية بنجاح:\n" + "\n".join(selected_courses)
        QMessageBox.information(self, 'نجاح', message)
    
    def create_schedule_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel('هنا سيتم عرض الجدول الدراسي للطالب')
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        widget.setLayout(layout)
        return widget

class AdminDashboard(QMainWindow):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'لوحة الإدارة - {self.user["name"]}')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        title = QLabel(f'لوحة إدارة النظام - {self.user["name"]}')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(title)
        
        # إضافة محتوى لوحة الإدارة
        content_label = QLabel('''<center>
        <h3>مهام المسؤول:</h3>
        <p>• إدارة المقررات الدراسية</p>
        <p>• إدارة الطلاب</p>
        <p>• متابعة التسجيلات</p>
        <p>• إعدادات النظام</p>
        </center>''')
        layout.addWidget(content_label)
        
        central_widget.setLayout(layout)

class MainApp:
    def __init__(self):
        self.db = Database()
        self.user_manager = UserManager(self.db)
        self.current_user = None
    
    def run(self):
        app = QApplication(sys.argv)
        
        # عرض نافذة تسجيل الدخول
        login_dialog = LoginDialog(self.user_manager)
        if login_dialog.exec_() == QDialog.Accepted:
            self.current_user = login_dialog.current_user
            
            # عرض لوحة التحكم المناسبة
            if self.current_user['role'] == 'student':
                dashboard = StudentDashboard(self.current_user, self.db)
            else:
                dashboard = AdminDashboard(self.current_user, self.db)
            
            dashboard.show()
            sys.exit(app.exec_())
        else:
            sys.exit()

if __name__ == '__main__':
    main_app = MainApp()
    main_app.run()
