# test.py
from database import Database
from models import UserManager

# اختبار قاعدة البيانات
print("جرب اختبار قاعدة البيانات...")
db = Database()
print("✓ قاعدة البيانات شغالة")

# اختبار UserManager
print("جرب اختبار UserManager...")
user_manager = UserManager(db)
print("✓ UserManager شغال")

# اختبار المصادقة
print("جرب اختبار Login...")
user = user_manager.authenticate("ADMIN001", "admin123")
if user:
    print(f"✓ Login ناجح! مرحباً {user['name']}")
else:
    print("✗ Login فاشل")

print("كل الاختبارات مكتملة!")