import sys
import random
import LIGHT
import DARK
import DB
import log_in
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QFrame,
    QMessageBox, QDialog, QLineEdit, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox,
    QGraphicsDropShadowEffect,
    QStatusBar,
    # (تمت إضافة أزرار الراديو ومجموعة الأزرار)
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor

LIGHT_MODE_QSS = """
QDialog, QWidget { background-color: #f0f2f5; font-family: "Arial", sans-serif; color: #333; }
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
QListWidget::item:disabled { color: #999; background-color: #f9f9f9; }
QStatusBar { color: #333; font-weight: bold; }
QPushButton[class="theme_button"] {
    background-color: #e0e0e0;
    color: #333;
    font-size: 16px; font-weight: bold;
    padding: 0px; margin-top: 0px;
    min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px;
    border-radius: 15px; /* دائري */
}
QPushButton[class="theme_button"]:hover { background-color: #d0d0d0; }

/* --- (جديد: تعديل زر الاختيار للوضع الفاتح) --- */
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 9px; /* دائري */
    border: 2px solid #999;
    background-color: #f0f0f0;
}
QRadioButton::indicator:hover {
    border: 2px solid #007bff; /* إطار أزرق عند التأشير */
}
QRadioButton::indicator:checked {
    border: 2px solid #007bff; /* إطار أزرق عند الاختيار */
    /* إنشاء نقطة زرقاء في المنتصف */
    background-color: qradialgradient(
        cx:0.5, cy:0.5, radius: 0.5, fx:0.5, fy:0.5, 
        stop:0.4 #007bff,  /* النقطة الزرقاء */
        stop:0.5 #f0f0f0   /* الخلفية البيضاء حولها */
    );
}
QRadioButton::indicator:disabled {
    border: 2px solid #ccc;
    background-color: #f9f9f9;
}
/* --- (نهاية التعديل) --- */
"""
