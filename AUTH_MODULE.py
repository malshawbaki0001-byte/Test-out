"""Auth Module - المصادقة"""

import re
import random
import time
import bcrypt
import smtplib
from email.message import EmailMessage
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFormLayout, QMessageBox, QApplication, QComboBox, QWidget, QFrame
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, Qt, QTimer
from CONTROLLERS import UserController, StudentController, CourseController
from DOMAIN_MODELS import DomainModels
from APP_MODULE import AppModule


class UserManager:
        def __init__(self):
            self.user_controller = Controllers.UserController()

        def Authenticate(self, identifier: str, password: str):
            return self.user_controller.authenticate(identifier, password)

        def CreateUser(self, user_id: str, email: str, password: str, role: str, display_name: str = "", mobile: str = ""):
            return self.user_controller.create_user(user_id, email, password, role, display_name, mobile)

        def CreateDefaultAdmin(self):
            return self.user_controller.create_default_admin()

    class StudentManager:
        def __init__(self):
            self.course_controller = Controllers.CourseController()
            self.student_controller = Controllers.StudentController(self.course_controller)

        def GetStudent(self, student_id: str):
            return self.student_controller.get_student(student_id)

        def GetAllStudentsDatabase(self):
            return self.student_controller.get_all_students()

        def DeleteStudent(self, student_id: str):
            self.student_controller.delete_student(student_id)

    class LoginDialog(QDialog):
        def __init__(self, user_manager: 'AuthModule.UserManager', parent=None):
            super().__init__(parent)
            self.user_manager = user_manager
            self.current_user = None
            self.is_dark_mode = False
            self.setWindowTitle('تسجيل الدخول - نظام ODUS')
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setGeometry(0, 0, 800, 600)
            self.InitUi()

        def InitUi(self):
            layout = QVBoxLayout(self)
            top_bar = QHBoxLayout()
            self.theme_button = QPushButton("🌙")
            self.theme_button.setProperty("class", "theme_button")
            self.theme_button.clicked.connect(self.ToggleTheme)
            top_bar.addWidget(self.theme_button)
            top_bar.addStretch()
            layout.addLayout(top_bar)
            login_frame = QFrame()
            login_frame.setProperty("class", "card")
            AppModule.ApplyShadow(login_frame)
            card_layout = QVBoxLayout(login_frame)
            title = QLabel("نظام التسجيل الجامعي")
            title.setObjectName("TitleLabel")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(title)
            form_layout = QFormLayout()
            self.id_input = QLineEdit()
            self.id_input.setPlaceholderText('المعرف')
            self.email_input = QLineEdit()
            self.email_input.setPlaceholderText("البريد الإلكتروني")
            self.pass_input = QLineEdit()
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.pass_input.setPlaceholderText('كلمة المرور')
            form_layout.addRow(QLabel("المعرف:"), self.id_input)
            form_layout.addRow(QLabel("البريد:"), self.email_input)
            form_layout.addRow(QLabel("كلمة المرور:"), self.pass_input)
            card_layout.addLayout(form_layout)
            self.forgot_password_btn = QPushButton("نسيت كلمة المرور؟")
            self.forgot_password_btn.setProperty("class", "secondary")
            self.forgot_password_btn.setStyleSheet("border: none; text-decoration: underline;")
            self.forgot_password_btn.clicked.connect(self.HandleForgotPassword)
            self.login_button = QPushButton('تسجيل الدخول')
            self.login_button.clicked.connect(self.HandleLogin)
            self.register_button = QPushButton('إنشاء حساب طالب جديد')
            self.register_button.setProperty("class", "secondary")
            self.register_button.clicked.connect(self.HandleRegister)
            card_layout.addWidget(self.login_button)
            card_layout.addWidget(self.register_button)
            card_layout.addWidget(self.forgot_password_btn)
            
            
            layout.addWidget(login_frame)

        def ToggleTheme(self):
            app = QApplication.instance()
            self.is_dark_mode = not self.is_dark_mode
            app.setStyleSheet(AppModule.DARK_MODE_QSS if self.is_dark_mode else AppModule.LIGHT_MODE_QSS)
            self.theme_button.setText("☀️" if self.is_dark_mode else "🌙")

        def HandleLogin(self):
            identifier = self.id_input.text().strip() or self.email_input.text().strip()
            password = self.pass_input.text()
            if not identifier or not password:
                QMessageBox.warning(self, 'خطأ', 'الرجاء إدخال البيانات!')
                return
            user = self.user_manager.authenticate(identifier, password)
            if user:
                self.current_user = user
                self.accept()
            else:
                QMessageBox.warning(self, 'خطأ', 'المعرف أو كلمة المرور غير صحيحة')

        def HandleForgotPassword(self):
            AuthModule.ForgotPasswordDialog(parent=self).exec()

        def HandleRegister(self):
            AuthModule.RegisterStudentDialog(self.user_manager, parent=self).exec()

    class ForgotPasswordDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("استعادة كلمة المرور")
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.otp = None
            self.user_id = None
            self.student_id = None
            self.email = None
            self.otp_expiry = None
            self.timer = QTimer(self)
            self.timer.setInterval(60000)
            self.timer.timeout.connect(self.AllowResendOtp)
            self.timer.setSingleShot(True)
            self.InitUi()

        def InitUi(self):
            layout = QVBoxLayout(self)
            layout.setSpacing(15)
            self.id_input = QLineEdit()
            self.id_input.setPlaceholderText("المعرف")
            self.email_input = QLineEdit()
            self.email_input.setPlaceholderText("البريد الإلكتروني")
            self.otp_input = QLineEdit()
            self.otp_input.setPlaceholderText("رمز OTP")
            self.otp_input.setEnabled(False)
            self.new_password_input = QLineEdit()
            self.new_password_input.setPlaceholderText("كلمة مرور جديدة")
            self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.new_password_input.setEnabled(False)
            self.send_otp_btn = QPushButton("إرسال OTP")
            self.send_otp_btn.clicked.connect(self.SendOtp)
            self.verify_otp_btn = QPushButton("تحقق من OTP")
            self.verify_otp_btn.clicked.connect(self.VerifyOtp)
            self.verify_otp_btn.setEnabled(False)
            self.reset_btn = QPushButton("تحديث كلمة المرور")
            self.reset_btn.clicked.connect(self.ResetPassword)
            self.reset_btn.setEnabled(False)
            for label, widget in [("المعرف:", self.id_input), ("البريد الإلكتروني:", self.email_input),
                                   ("رمز OTP:", self.otp_input), ("كلمة المرور الجديدة:", self.new_password_input)]:
                layout.addWidget(QLabel(label))
                layout.addWidget(widget)
                if label=="البريد الإلكتروني:" :
                    layout.addWidget(self.send_otp_btn)
                if label == "رمز OTP:":
                    layout.addWidget(self.verify_otp_btn)
                if label == "كلمة المرور الجديدة:":
                    layout.addWidget(self.reset_btn)

        def SendOtp(self):
            identifier = self.id_input.text().strip()
            self.email = self.email_input.text().strip()
            if not identifier or not self.email:
                QMessageBox.warning(self, "خطأ", "أدخل المعرف والبريد!")
                return
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email):
                QMessageBox.warning(self, "خطأ", "البريد الإلكتروني غير صالح!")
                return
            try:
                from DATABASE_LAYER import DatabaseLayer
                conn = DatabaseLayer.GetConnection()
                cur = conn.cursor()
                cur.execute("""SELECT u.user_id, u.student_id, u.email, u.role FROM users u
                                LEFT JOIN students s ON u.student_id = s.student_id
                                WHERE (u.student_id = ? OR u.email = ? OR CAST(u.user_id AS TEXT) = ?) AND u.email = ?""",
                            (identifier, identifier, identifier, self.email))
                user = cur.fetchone()
                if not user:
                    conn.close()
                    QMessageBox.warning(self, "خطأ", "المعرف أو البريد غير صحيحين!")
                    return
                self.user_id = user[0]
                self.student_id = user[1]
                actual_email = user[2]
                if actual_email.lower() != self.email.lower():
                    conn.close()
                    QMessageBox.warning(self, "خطأ", "البريد الإلكتروني لا يطابق المعرف!")
                    return
                conn.close()
                self.otp = str(random.randint(100000, 999999))
                self.otp_expiry = time.time() + 180
                self.SendEmail(self.email, self.otp)
                self.otp_input.setEnabled(True)
                self.verify_otp_btn.setEnabled(True)
                self.send_otp_btn.setEnabled(False)
                self.timer.start()
                QMessageBox.information(self, "نجاح", f"تم إرسال OTP إلى {self.email}.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل العملية: {e}")

        def AllowResendOtp(self):
            self.send_otp_btn.setEnabled(True)

        def VerifyOtp(self):
            if not self.otp_expiry or time.time() > self.otp_expiry:
                QMessageBox.warning(self, "خطأ", "انتهت صلاحية OTP!")
                return
            if self.otp_input.text() == self.otp:
                self.new_password_input.setEnabled(True)
                self.reset_btn.setEnabled(True)
                QMessageBox.information(self, "نجاح", "أدخل كلمة مرور جديدة.")
            else:
                QMessageBox.warning(self, "خطأ", "OTP خاطئ!")

        def ResetPassword(self):
            new_pw = self.new_password_input.text()
            if not new_pw or len(new_pw) < 8:
                QMessageBox.warning(self, "خطأ", "كلمة المرور يجب أن تحتوي على 8+ خانات!")
                return
            if not (any(c.isdigit() for c in new_pw) and any(c.isalpha() for c in new_pw)):
                QMessageBox.warning(self, "خطأ", "كلمة المرور تحتاج أرقام + حروف!")
                return
            if not self.user_id:
                QMessageBox.warning(self, "خطأ", "أعد المحاولة من البداية!")
                return
            try:
                password_hash = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                from DATABASE_LAYER import DatabaseLayer
                conn = DatabaseLayer.GetConnection()
                cur = conn.cursor()
                cur.execute("UPDATE users SET password_hash=? WHERE user_id=?", (password_hash, self.user_id))
                if cur.rowcount == 0:
                    conn.close()
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على المستخدم!")
                    return
                conn.commit()
                conn.close()
                QMessageBox.information(self, "نجاح", "تم تحديث كلمة المرور!")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل التحديث: {e}")

        def SendEmail(self, to_email, otp):
            EMAIL = 'ee202teama@gmail.com'
            PASSWORD = 'uggojcwzdclhqalm'
            msg = EmailMessage()
            msg['From'] = EMAIL
            msg['To'] = to_email
            msg['Subject'] = 'OTP كلمة المرور لمرة واحدة'
            msg.set_content(f"رمز OTP الخاص بك: {otp}\n\nهذا الرمز صالح لمدة 3 دقائق.")
            try:
                with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
                    server.starttls()
                    server.login(EMAIL, PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"فشل إرسال البريد: {e}")

    class RegisterStudentDialog(QDialog):
        def __init__(self, user_manager: 'AuthModule.UserManager', parent=None):
            super().__init__(parent)
            self.user_manager = user_manager
            self.setWindowTitle('إنشاء حساب طالب جديد')
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setModal(True)
            self.setGeometry(0, 0, 600, 500)
            self.InitUi()

        def InitUi(self):
            card_widget = QWidget()
            card_widget.setProperty("class", "card")
            card_widget.setFixedWidth(400)
            card_widget.setFixedHeight(450)
            AppModule.ApplyShadow(card_widget)
            card_layout = QVBoxLayout(card_widget)
            card_layout.setContentsMargins(30, 30, 30, 30)
            card_layout.setSpacing(15)
            title = QLabel('إنشاء حساب طالب جديد')
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setObjectName("TitleLabel")
            card_layout.addWidget(title)
            form_layout = QFormLayout()
            self.name_input = QLineEdit()
            self.email_input = QLineEdit()
            self.mobile_input = QLineEdit()
            mobile_validator = QRegularExpressionValidator(QRegularExpression("^05[0-9]{8}$"))
            self.mobile_input.setValidator(mobile_validator)
            self.mobile_input.setPlaceholderText("05XXXXXXXX")
            self.mobile_input.setMaxLength(10)
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.program_combo = QComboBox()
            self.program_combo.addItems(['Computer', 'Communications', 'Power', 'Biomedical'])
            self.level_combo = QComboBox()
            self.level_combo.addItems([str(i) for i in range(1, 11)])
            form_layout.addRow('الاسم الكامل:', self.name_input)
            form_layout.addRow('البريد الإلكتروني:', self.email_input)
            form_layout.addRow('رقم الجوال:', self.mobile_input)
            form_layout.addRow('كلمة المرور:', self.password_input)
            form_layout.addRow('البرنامج:', self.program_combo)
            form_layout.addRow('المستوى الحالي:', self.level_combo)
            card_layout.addLayout(form_layout)
            card_layout.addStretch()
            self.register_button = QPushButton('إنشاء الحساب')
            self.register_button.clicked.connect(self.CreateAccount)
            card_layout.addWidget(self.register_button)
            main_layout = QHBoxLayout(self)
            main_layout.addStretch()
            main_layout.addWidget(card_widget)
            main_layout.addStretch()

        def CreateAccount(self):
            new_password = self.password_input.text()
            name = self.name_input.text().strip()
            email = self.email_input.text().strip()
            mobile = self.mobile_input.text().strip()
            if not name or not email or not mobile or not new_password:
                QMessageBox.warning(self, 'خطأ', 'الرجاء ملء جميع الحقول')
                return
            if not mobile.startswith('05') or len(mobile) != 10 or not mobile.isdigit():
                QMessageBox.warning(self, 'خطأ', 'رقم الجوال يجب أن يبدأ بـ 05 ويتكون من 10 أرقام فقط')
                return
            user_id = None
            for attempts in range(1000):
                prefix = random.choice(['16', '27'])
                candidate_id = f"{prefix}{random.randint(10000, 99999)}"
                from DATABASE_LAYER import DatabaseLayer
                if not DatabaseLayer.StudentRepository.StudentExists(candidate_id):
                    user_id = candidate_id
                    break
            if user_id is None:
                QMessageBox.critical(self, 'خطأ', 'فشل توليد معرف فريد. يرجى المحاولة مرة أخرى.')
                return
            if not (len(new_password) >= 8 and any(c.isdigit() for c in new_password) and any(c.isalpha() for c in new_password)):
                QMessageBox.warning(self, 'خطأ', 'كلمة المرور يجب أن تحتوي على 8+ خانات، أرقام، وحروف.')
                return
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                QMessageBox.warning(self, 'خطأ', 'البريد الإلكتروني غير صالح!')
                return
            program = self.program_combo.currentText()
            program_for_db = 'Comm' if program == 'Communications' else program
            level = int(self.level_combo.currentText())
            from CONTROLLERS import Controllers
            course_ctrl = Controllers.CourseController()
            student_ctrl = Controllers.StudentController(course_ctrl)
            success, message = student_ctrl.AddStudent(user_id, name, email, program_for_db, level)
            if not success:
                QMessageBox.critical(self, 'خطأ في التسجيل', message)
                return
            success, message = self.user_manager.CreateUser(user_id, email, new_password, "student", name, mobile)
            if not success:
                QMessageBox.critical(self, 'خطأ', f'فشل إنشاء الحساب: {message}')
                return
            QMessageBox.information(self, 'تم إنشاء الحساب بنجاح',
                                   f"المعرف الجامعي: {user_id}\nكلمة المرور: {new_password}\nالبرنامج: {program} - المستوى {level}\n{message}")
            self.accept()