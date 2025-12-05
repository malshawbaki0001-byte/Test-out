"""
================================================================================
App Module - التطبيق الرئيسي + الأنماط
================================================================================

يحتوي على:
- الأنماط (LIGHT_MODE_QSS, DARK_MODE_QSS)
- دالة ApplyShadow
- MainApp (التطبيق الرئيسي)
- MainWindow (النافذة الرئيسية)
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect, QWidget, QDialog, QMessageBox
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class AppModule:
    """كلاس التطبيق الرئيسي + الأنماط"""
    
    # ========================================================================
    # STYLES
    # ========================================================================
    
    LIGHT_MODE_QSS = """
QDialog, QWidget, QMainWindow { background-color: #f0f2f5; font-family: "Arial", sans-serif; color: #333; }
QFrame[class="card"], QWidget[class="card"] { background-color: #ffffff; border-radius: 10px; }
QLabel { font-size: 14px; font-weight: bold; color: #333; }
QLabel#TitleLabel { font-size: 24px; font-weight: bold; color: #003366; }
QLineEdit, QComboBox {
    font-size: 14px; padding: 10px 15px; border: 1px solid #d0d0d0;
    border-radius: 5px; background-color: #fafafa; color: black;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #007bff; }
QPushButton {
    font-size: 14px; font-weight: bold; color: white;
    padding: 12px; border-radius: 5px; border: none; margin-top: 5px;
    background-color: #007bff; 
}
QPushButton:hover { background-color: #0056b3; }
QPushButton[class="secondary"] { background-color: #6c757d; }
QPushButton[class="secondary"]:hover { background-color: #5a6268; }
QPushButton[class="danger"] { background-color: #dc3545; }
QPushButton[class="danger"]:hover { background-color: #c82333; }
QTableWidget {
    background-color: #ffffff; border: 1px solid #d0d0d0;
    border-radius: 5px; font-size: 13px;
    selection-background-color: #007bff; selection-color: white;
}
QHeaderView::section {
    background-color: #f8f9fa; padding: 8px; border: none;
    border-bottom: 1px solid #d0d0d0; font-weight: bold;
}
QListWidget {
    background-color: #ffffff; border: 1px solid #d0d0d0;
    border-radius: 5px; font-size: 14px;
}
QListWidget::item { padding: 10px; }
QListWidget::item:selected { background-color: #007bff; color: white; }
QStatusBar { color: #333; font-weight: bold; }
QPushButton[class="theme_button"] {
    background-color: #e0e0e0; color: #333;
    font-size: 16px; font-weight: bold;
    min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px;
    border-radius: 15px;
}
"""
    
    DARK_MODE_QSS = """
QDialog, QWidget, QMainWindow { background-color: #2b2b2b; font-family: "Arial", sans-serif; color: #f0f0f0; }
QFrame[class="card"], QWidget[class="card"] { background-color: #3c3c3c; border-radius: 10px; }
QLabel { font-size: 14px; font-weight: bold; color: #f0f0f0; }
QLabel#TitleLabel { font-size: 24px; font-weight: bold; color: #aaccff; }
QLineEdit, QComboBox {
    font-size: 14px; padding: 10px 15px; border: 1px solid #555;
    border-radius: 5px; background-color: #444; color: #f0f0f0;
}
QLineEdit:focus, QComboBox:focus { border: 1px solid #007bff; }
QPushButton {
    font-size: 14px; font-weight: bold; color: white;
    padding: 12px; border-radius: 5px; border: none; margin-top: 5px;
    background-color: #007bff;
}
QPushButton:hover { background-color: #0056b3; }
QPushButton[class="secondary"] { background-color: #6c757d; }
QPushButton[class="secondary"]:hover { background-color: #5a6268; }
QPushButton[class="danger"] { background-color: #dc3545; }
QPushButton[class="danger"]:hover { background-color: #c82333; }
QTableWidget {
    background-color: #3c3c3c; border: 1px solid #555;
    border-radius: 5px; font-size: 13px;
    selection-background-color: #007bff; selection-color: white;
}
QHeaderView::section {
    background-color: #444; padding: 8px; border: none;
    border-bottom: 1px solid #555; font-weight: bold; color: #f0f0f0;
}
QListWidget {
    background-color: #3c3c3c; border: 1px solid #555;
    border-radius: 5px; font-size: 14px;
}
QListWidget::item { padding: 10px; }
QListWidget::item:selected { background-color: #007bff; color: white; }
QStatusBar { color: #f0f0f0; font-weight: bold; }
QPushButton[class="theme_button"] {
    background-color: #555; color: #f0f0f0;
    font-size: 16px; font-weight: bold;
    min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px;
    border-radius: 15px;
    margin-left: 10px;  
}
"""
    
    @staticmethod
    def ApplyShadow(widget: QWidget) -> None:
        """
        تطبيق تأثير الظل على الويدجت
        
        Args:
            widget: الويدجت المراد تطبيق الظل عليه
        """
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        widget.setGraphicsEffect(shadow)
    
    # ========================================================================
    # MAIN WINDOW
    # ========================================================================
    
    class MainWindow(QMainWindow):
        """النافذة الرئيسية - تدير الواجهة الرسومية الشاملة"""
        def __init__(self, parent: Optional[QWidget] = None) -> None:
            """
            تهيئة النافذة الرئيسية
            
            Args:
                parent: الويدجت الأب (اختياري)
            """
            super().__init__(parent)
            self.setWindowTitle('نظام التسجيل الجامعي - ODUS')
            self.setGeometry(100, 100, 1200, 800)
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            
            # Import here to avoid circular imports
            from AUTH_MODULE import UserManager, StudentManager
            from DATABASE_LAYER import DatabaseLayer

            self.user_manager = UserManager()
            self.student_manager = StudentManager()
            self.doctor_manager = DatabaseLayer.DoctorManager()

            from CONTROLLERS import DoctorController
            doctor_controller = DoctorController(None)

            # إنشاء حساب مدير افتراضي إذا لم يكن موجوداً
            self.user_manager.CreateDefaultAdmin()

            # إنشاء حساب دكتور افتراضي إذا لم يكن موجوداً
            doctor_controller.CreateDefaultDoctor()
            
            # Current dashboard
            self.current_dashboard: Optional[QWidget] = None
            self.is_dark_mode: bool = False
        
        def ShowLogin(self) -> None:
            """
            عرض شاشة تسجيل الدخول
            
            يعرض نافذة تسجيل الدخول ويوجه المستخدم إلى لوحة التحكم المناسبة
            بناءً على نوع المستخدم (طالب أو مدير)
            """
            from AUTH_MODULE import LoginDialog

            login = LoginDialog(self.user_manager, parent=self)
            result = login.exec()
            
            if result == QDialog.DialogCode.Accepted:
                from DOMAIN_MODELS import DomainModels
                user: Optional[DomainModels.User] = login.current_user
                if not user:
                    return
                    
                self.is_dark_mode = login.is_dark_mode
                
                # Apply theme
                app = QApplication.instance()
                if app:
                    if self.is_dark_mode:
                        app.setStyleSheet(AppModule.DARK_MODE_QSS)
                    else:
                        app.setStyleSheet(AppModule.LIGHT_MODE_QSS)
                
                # Show appropriate dashboard
                try:
                    if user.IsStudent():
                        self.ShowStudentDashboard(user)
                    elif user.IsAdmin():
                        self.ShowAdminDashboard(user)
                    elif user.IsDoctor():
                        self.ShowDoctorDashboard(user)
                    else:
                        QMessageBox.warning(self, "خطأ", "نوع المستخدم غير معروف")
                except Exception as e:
                    QMessageBox.critical(self, "خطأ", f"حدث خطأ: {str(e)}")
        
        def ShowStudentDashboard(self, user: 'DomainModels.User') -> None:
            """
            عرض لوحة تحكم الطالب
            
            Args:
                user: كائن المستخدم (طالب)
            """
            from STUDENT_MODULE import Dashboard

            student = self.student_manager.GetStudent(user.user_id)
            if not student:
                QMessageBox.critical(self, "خطأ", "تعذر تحميل بيانات الطالب")
                return

            # Remove previous dashboard
            if self.current_dashboard:
                self.setCentralWidget(None)
                self.current_dashboard.deleteLater()

            # Create and show student dashboard
            dashboard = Dashboard(student)
            dashboard.is_dark_mode = self.is_dark_mode
            if self.is_dark_mode and hasattr(dashboard, 'theme_button'):
                dashboard.theme_button.setText("☀️")
            
            self.setCentralWidget(dashboard)
            self.current_dashboard = dashboard
        
        def ShowAdminDashboard(self, user: 'DomainModels.User') -> None:
            """
            عرض لوحة تحكم المدير
            
            Args:
                user: كائن المستخدم (مدير)
            """
            from ADMIN_MODULE import AdminDashboard
            
            # Remove previous dashboard
            if self.current_dashboard:
                self.setCentralWidget(None)
                self.current_dashboard.deleteLater()
            
            # Create and show admin dashboard
            dashboard = AdminDashboard(user)
            dashboard.is_dark_mode = self.is_dark_mode
            if self.is_dark_mode and hasattr(dashboard, 'theme_button'):
                dashboard.theme_button.setText("☀️")
            
            self.setCentralWidget(dashboard)
            self.current_dashboard = dashboard

        def ShowDoctorDashboard(self, user: 'DomainModels.User') -> None:
            """
            عرض لوحة تحكم الدكتور

            Args:
                user: كائن المستخدم (دكتور)
            """
            from DOCTOR_MODULE import DoctorModule
            from DOMAIN_MODELS import DomainModels

            # جلب بيانات الدكتور من قاعدة البيانات
            doctor_data = self.doctor_manager.GetDoctor(user.user_id)
            if not doctor_data:
                QMessageBox.critical(self, "خطأ", "تعذر تحميل بيانات الدكتور")
                return

            # إنشاء كائن الدكتور
            doctor = DomainModels.Doctor(
                doctor_id=doctor_data['doctor_id'],
                name=doctor_data['name'],
                email=doctor_data['email'],
                preferred_courses=doctor_data['preferred_courses'],
                time_availability=doctor_data['time_availability']
            )

            # Remove previous dashboard
            if self.current_dashboard:
                self.setCentralWidget(None)
                self.current_dashboard.deleteLater()

            # Create and show doctor dashboard
            dashboard = DoctorModule.Dashboard(doctor)
            dashboard.is_dark_mode = self.is_dark_mode
            if self.is_dark_mode and hasattr(dashboard, 'theme_button'):
                dashboard.theme_button.setText("☀️")

            self.setCentralWidget(dashboard)
            self.current_dashboard = dashboard

    # ========================================================================
    # MAIN APP
    # ========================================================================
    
    class MainApp(QApplication):
        """التطبيق الرئيسي - نقطة الدخول للتطبيق"""
        def __init__(self, argv: list) -> None:
            """
            تهيئة التطبيق الرئيسي
            
            Args:
                argv: قائمة معاملات سطر الأوامر
            """
            super().__init__(argv)
            self.setStyleSheet(AppModule.LIGHT_MODE_QSS)
        
        def Run(self) -> int:
            """تشغيل حلقة التطبيق الرئيسية"""
            try:
                main_window = AppModule.MainWindow()
                main_window.show()
                main_window.ShowLogin()
                return self.exec()
            except Exception as e:
                print(f"Error running application: {e}")
                return 1


if __name__ == '__main__':
    try:
        app = AppModule.MainApp(sys.argv)
        sys.exit(app.Run())
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)