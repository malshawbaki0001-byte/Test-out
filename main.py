import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
                             QTabWidget, QMessageBox, QDialog, QFormLayout, QGroupBox, 
                             QTextEdit, QHeaderView, QComboBox, QListWidget, QListWidgetItem,
                             QSpinBox, QFrame)
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
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel('نظام تسجيل المقررات الدراسية')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # إطار تسجيل الدخول
        login_frame = QFrame()
        login_frame.setFrameStyle(QFrame.Box)
        login_frame.setStyleSheet("QFrame { border: 2px solid #3498db; border-radius: 10px; padding: 20px; }")
        login_layout = QVBoxLayout(login_frame)
        
        login_title = QLabel('تسجيل الدخول')
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setFont(QFont('Arial', 14, QFont.Bold))
        login_title.setStyleSheet("color: #3498db; margin-bottom: 15px;")
        login_layout.addWidget(login_title)
        
        # نموذج تسجيل الدخول
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("أدخل رقم المستخدم")
        self.user_id_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        form_layout.addRow('رقم المستخدم:', self.user_id_input)
        form_layout.addRow('كلمة المرور:', self.password_input)
        
        login_layout.addLayout(form_layout)
        
        # أزرار تسجيل الدخول
        login_button_layout = QHBoxLayout()
        
        login_btn = QPushButton('تسجيل الدخول')
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                font-weight: bold; 
                padding: 10px; 
                border: none; 
                border-radius: 5px; 
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        login_button_layout.addWidget(login_btn)
        login_layout.addLayout(login_button_layout)
        
        layout.addWidget(login_frame)
        
        # فاصل
        separator = QLabel("أو")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #7f8c8d; margin: 10px 0;")
        layout.addWidget(separator)
        
        # زر إنشاء حساب جديد
        create_account_btn = QPushButton('إنشاء حساب طالب جديد')
        create_account_btn.clicked.connect(self.show_registration)
        create_account_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                font-weight: bold; 
                padding: 12px; 
                border: none; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        layout.addWidget(create_account_btn)
        
        # بيانات الدخول الافتراضية
        info_label = QLabel('''بيانات الدخول الافتراضية:
        المسؤول: ADMIN001 / admin123
        الطالب: STU001 / student123''')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #7f8c8d; font-size: 10px; margin-top: 15px; background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
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
    
    def show_registration(self):
        dialog = StudentRegistrationDialog(self.user_manager)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, 'نجاح', 'تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.')

class StudentRegistrationDialog(QDialog):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('إنشاء حساب طالب جديد')
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        
        # العنوان
        title = QLabel('إنشاء حساب طالب جديد')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # نموذج التسجيل
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(15)
        
        # معلومات الطالب
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل الاسم الكامل")
        self.name_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@domain.com")
        self.email_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("أدخل كلمة مرور قوية")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("أعد إدخال كلمة المرور")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        self.program_combo = QComboBox()
        self.program_combo.addItems(['Computer', 'Communications', 'Power', 'Biomedical'])
        self.program_combo.setStyleSheet("QComboBox { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 5)
        self.level_spin.setValue(1)
        self.level_spin.setStyleSheet("QSpinBox { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2025)
        self.year_spin.setValue(2024)
        self.year_spin.setStyleSheet("QSpinBox { padding: 8px; border: 1px solid #bdc3c7; border-radius: 5px; }")
        
        # إضافة الحقول إلى النموذج
        form_layout.addRow('الاسم الكامل:', self.name_input)
        form_layout.addRow('البريد الإلكتروني:', self.email_input)
        form_layout.addRow('كلمة المرور:', self.password_input)
        form_layout.addRow('تأكيد كلمة المرور:', self.confirm_password_input)
        form_layout.addRow('التخصص:', self.program_combo)
        form_layout.addRow('المستوى:', self.level_spin)
        form_layout.addRow('سنة التسجيل:', self.year_spin)
        
        layout.addLayout(form_layout)
        
        # زر إنشاء الحساب
        register_btn = QPushButton('إنشاء الحساب')
        register_btn.clicked.connect(self.register_student)
        register_btn.setStyleSheet("""
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                font-weight: bold; 
                padding: 12px; 
                border: none; 
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        layout.addWidget(register_btn)
        
        # زر إلغاء
        cancel_btn = QPushButton('إلغاء')
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton { 
                background-color: #95a5a6; 
                color: white; 
                font-weight: bold; 
                padding: 10px; 
                border: none; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        layout.addWidget(cancel_btn)
        
        self.setLayout(layout)
    
    def register_student(self):
        # جمع البيانات
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        program = self.program_combo.currentText()
        level = self.level_spin.value()
        year = self.year_spin.value()
        
        # التحقق من البيانات
        if not all([name, email, password, confirm_password]):
            QMessageBox.warning(self, 'خطأ', 'يرجى ملء جميع الحقول')
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, 'خطأ', 'كلمتا المرور غير متطابقتين')
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, 'خطأ', 'كلمة المرور يجب أن تكون 6 أحرف على الأقل')
            return
        
        # توليد رقم طالب تلقائي
        program_code = program[:3].upper()
        student_id = self.user_manager.generate_student_id(program_code, year)
        
        # تحضير بيانات الطالب
        student_data = {
            'student_id': student_id,
            'name': name,
            'email': email,
            'password': password,
            'program': program,
            'level': level,
            'registration_year': year
        }
        
        # إنشاء الحساب
        success, message = self.user_manager.register_student(student_data)
        
        if success:
            QMessageBox.information(self, 'نجاح', f'{message}\nرقم الطالب الخاص بك: {student_id}')
            self.accept()
        else:
            QMessageBox.warning(self, 'خطأ', message)

# ... (بقية الكود يبقى كما هو من الإصدار السابق - StudentDashboard و AdminDashboard)

class StudentDashboard(QMainWindow):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.user_manager = UserManager(db)
        self.reg_system = RegistrationSystem(db)
        self.student = self.user_manager.get_student_profile(user['user_id'])
        self.semester = "2024-Fall"
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'لوحة الطالب - {self.user["name"]}')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # شريط المعلومات
        info_bar = QWidget()
        info_bar.setStyleSheet("background-color: #34495e; color: white; padding: 10px; border-radius: 5px;")
        info_layout = QHBoxLayout(info_bar)
        
        student_info = QLabel(f'مرحباً {self.user["name"]} | {self.student.program} | المستوى {self.student.current_level} | سنة التسجيل: {self.student.registration_year}')
        student_info.setStyleSheet("color: white; font-size: 14px;")
        info_layout.addWidget(student_info)
        
        logout_btn = QPushButton('تسجيل الخروج')
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 3px; }")
        info_layout.addWidget(logout_btn)
        
        layout.addWidget(info_bar)
        
        # تبويبات
        tabs = QTabWidget()
        
        # تبويب التسجيل
        register_tab = self.create_register_tab()
        tabs.addTab(register_tab, "🎓 تسجيل المقررات")
        
        # تبويب الجدول الدراسي
        schedule_tab = self.create_schedule_tab()
        tabs.addTab(schedule_tab, "📅 جدولي الدراسي")
        
        # تبويب السجل الدراسي
        transcript_tab = self.create_transcript_tab()
        tabs.addTab(transcript_tab, "📊 سجلي الدراسي")
        
        # تبويب الملف الشخصي
        profile_tab = self.create_profile_tab()
        tabs.addTab(profile_tab, "👤 الملف الشخصي")
        
        layout.addWidget(tabs)
        central_widget.setLayout(layout)
    
    def create_profile_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # معلومات الطالب
        profile_group = QGroupBox("المعلومات الشخصية")
        profile_layout = QFormLayout()
        
        profile_layout.addRow('رقم الطالب:', QLabel(self.student.student_id))
        profile_layout.addRow('الاسم:', QLabel(self.student.name))
        profile_layout.addRow('البريد الإلكتروني:', QLabel(self.student.email))
        profile_layout.addRow('التخصص:', QLabel(self.student.program))
        profile_layout.addRow('المستوى:', QLabel(str(self.student.current_level)))
        profile_layout.addRow('سنة التسجيل:', QLabel(str(self.student.registration_year)))
        
        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)
        
        # الإحصائيات
        stats_group = QGroupBox("الإحصائيات")
        stats_layout = QVBoxLayout()
        
        completed_credits = self.student.get_completed_credits(self.db)
        current_courses = self.student.get_current_schedule(self.db, self.semester)
        current_credits = sum(course.credits for course in current_courses)
        
        stats_text = QTextEdit()
        stats_text.setPlainText(f'''إحصائياتك الدراسية:

الساعات المكتملة: {completed_credits} ساعة
الساعات المسجلة حالياً: {current_credits} ساعة
المقررات المسجلة: {len(current_courses)} مقرر
المستوى الحالي: {self.student.current_level}
التخصص: {self.student.program}''')
        stats_text.setReadOnly(True)
        
        stats_layout.addWidget(stats_text)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        widget.setLayout(layout)
        return widget
    
    def logout(self):
        reply = QMessageBox.question(self, 'تسجيل الخروج', 
                                   'هل أنت متأكد من تسجيل الخروج؟',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.close()
            # إعادة فتح نافذة تسجيل الدخول
            app = QApplication.instance()
            login_dialog = LoginDialog(UserManager(self.db))
            if login_dialog.exec_() == QDialog.Accepted:
                current_user = login_dialog.current_user
                if current_user['role'] == 'student':
                    student_profile = UserManager(self.db).get_student_profile(current_user['user_id'])
                    if student_profile:
                        dashboard = StudentDashboard(current_user, self.db)
                        dashboard.show()
    
    # ... (بقية دوال StudentDashboard تبقى كما هي)

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
            from admin_dashboard import AdminDashboard  # ستحتاج لإنشاء هذا الملف
            dashboard = AdminDashboard(current_user, db)
            dashboard.show()
        
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__ == "__main__":
    main()
