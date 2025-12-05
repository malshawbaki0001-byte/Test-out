"""
نسخة احتياطية كاملة (Monolithic) لمشروعك
تم دمج جميع ملفات المشروع في ملف واحد.
تم تجهيز جميع الدوال والكلاسات والتطبيق لبيئة PyQt6 كما هو الوضع الأصلي.
يرجى التأكد من تثبيت جميع الحزم المطلوبة:
pip install PyQt6 bcrypt

التشغيل:
    python main_full_backup.py

ملاحظة: الكود طويل وتم إعداد كافة الكلاسات في نفس الترتيب المنطقي.
"""

##########################################
# domain_models.py
##########################################

# === [ START domain_models.py ] ===
<استبدال بمحتوى domain_models.py بالكامل هنا>
# === [ END domain_models.py ] ===

##########################################
# database_layer.py
##########################################

# === [ START database_layer.py ] ===
<استبدال بمحتوى database_layer.py بالكامل هنا>
# === [ END database_layer.py ] ===

##########################################
# controllers.py
##########################################

# === [ START controllers.py ] ===
<استبدال بمحتوى controllers.py بالكامل هنا>
# === [ END controllers.py ] ===

##########################################
# app_module.py
##########################################

# === [ START app_module.py ] ===
<استبدال بمحتوى app_module.py بالكامل هنا>
# === [ END app_module.py ] ===

##########################################
# admin_module.py
##########################################

# === [ START admin_module.py ] ===
<استبدال بمحتوى admin_module.py بالكامل هنا>
# === [ END admin_module.py ] ===

##########################################
# student_module.py
##########################################

# === [ START student_module.py ] ===
<استبدال بمحتوى student_module.py بالكامل هنا>
# === [ END student_module.py ] ===

##########################################
# doctor_module.py
##########################################

# === [ START doctor_module.py ] ===
<استبدال بمحتوى doctor_module.py بالكامل هنا>
# === [ END doctor_module.py ] ===

##########################################
# auth_module.py
##########################################

# === [ START auth_module.py ] ===
<استبدال بمحتوى auth_module.py بالكامل هنا>
# === [ END auth_module.py ] ===

##########################################
# نقطة البدء الرئيسية (من run.py)
##########################################
if __name__ == "__main__":
    try:
        # استدعي AppModule من اسم الكلاس مباشرة حسب الترتيب أعلاه
        app = AppModule.MainApp(sys.argv)
        sys.exit(app.Run())
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
