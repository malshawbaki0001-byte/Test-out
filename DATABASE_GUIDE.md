# دليل استخدام طبقة قاعدة البيانات (DATABASE_LAYER.py)

## مرحباً بك في دليل المبتدئين! 👋

هذا الدليل سيشرح لك كيفية استخدام ملف قاعدة البيانات المبسط بطريقة سهلة وواضحة.

## 📋 ما هي قاعدة البيانات؟

قاعدة البيانات هي مكان نحفظ فيه البيانات بشكل منظم. في هذا المشروع نستخدم SQLite وهي قاعدة بيانات بسيطة جداً.

## 🗂️ الجداول في قاعدة البيانات

لدينا هذه الجداول الأساسية:

### 1. جدول المقررات (courses)
```sql
- course_code: رمز المقرر (مثل: EE202)
- name: اسم المقرر
- credits: عدد الساعات المعتمدة
- lecture_hours: ساعات المحاضرات
- lab_hours: ساعات المختبر
- level: المستوى الدراسي
```

### 2. جدول الشعب (sections)
```sql
- section_id: معرف الشعبة (مثل: EE202-01)
- course_code: رمز المقرر
- instructor: اسم المدرس
- start_time: وقت البداية (بالساعات)
- end_time: وقت النهاية (بالساعات)
- hall: قاعة المحاضرة
- max_capacity: السعة القصوى
- current_enrollment: عدد المسجلين الحالي
- days: أيام المحاضرة
```

### 3. جدول الطلاب (students)
```sql
- student_id: رقم الطالب الجامعي
- name: اسم الطالب
- email: البريد الإلكتروني
- program: البرنامج الدراسي
- level: المستوى الدراسي الحالي
```

### 4. جدول المستخدمين (users)
```sql
- user_id: معرف فريد للمستخدم
- student_id: رقم الطالب (إذا كان طالباً)
- email: البريد الإلكتروني
- password_hash: كلمة المرور المشفرة
- role: الدور (student أو admin)
- display_name: الاسم المعروض
- mobile: رقم الجوال
```

## 🚀 كيفية استخدام الكلاسات

### مثال 1: إضافة طالب جديد

```python
from DATABASE_LAYER import DatabaseLayer

# إضافة طالب جديد
success = DatabaseLayer.StudentManager.AddStudent(
    student_id="27123456",
    name="أحمد محمد",
    email="ahmed@example.com",
    program="Computer",
    level=1
)

if success:
    print("✅ تم إضافة الطالب بنجاح!")
else:
    print("❌ فشل في إضافة الطالب")
```

### مثال 2: جلب بيانات طالب

```python
from DATABASE_LAYER import DatabaseLayer

# جلب بيانات طالب
student = DatabaseLayer.StudentManager.GetStudent("27123456")

if student:
    print(f"اسم الطالب: {student['name']}")
    print(f"بريده الإلكتروني: {student['email']}")
    print(f"برنامجه: {student['program']}")
else:
    print("الطالب غير موجود")
```

### مثال 3: إضافة مقرر جديد

```python
from DATABASE_LAYER import DatabaseLayer

# إضافة مقرر جديد
success = DatabaseLayer.CourseManager.AddCourse(
    course_code="EE202",
    name="دوائر كهربائية",
    credits=3,
    lecture_hours=2,
    lab_hours=1,
    level=2
)

if success:
    print("✅ تم إضافة المقرر بنجاح!")
else:
    print("❌ المقرر موجود مسبقاً")
```

### مثال 4: جلب جميع المقررات

```python
from DATABASE_LAYER import DatabaseLayer

# جلب جميع المقررات
courses = DatabaseLayer.CourseManager.GetAllCourses()

print(f"عدد المقررات: {len(courses)}")
for course in courses:
    print(f"- {course['course_code']}: {course['name']}")
```

### مثال 5: إضافة شعبة جديدة

```python
from DATABASE_LAYER import DatabaseLayer

# إضافة شعبة جديدة
success = DatabaseLayer.SectionManager.AddSection(
    section_id="EE202-01",
    course_code="EE202",
    instructor="د. محمد أحمد",
    start_time=8,
    end_time=10,
    hall="قاعة 101",
    max_capacity=30,
    days="الأحد,الثلاثاء"
)

if success:
    print("✅ تم إضافة الشعبة بنجاح!")
else:
    print("❌ الشعبة موجودة مسبقاً")
```

### مثال 6: تسجيل طالب في شعبة

```python
from DATABASE_LAYER import DatabaseLayer
import datetime

# تسجيل طالب في شعبة
registration_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

success = DatabaseLayer.StudentManager.RegisterForSection(
    student_id="27123456",
    section_id="EE202-01",
    registration_time=registration_time
)

if success:
    print("✅ تم التسجيل بنجاح!")
else:
    print("❌ فشل في التسجيل")
```

### مثال 7: إنشاء مستخدم جديد

```python
from DATABASE_LAYER import DatabaseLayer
import bcrypt

# إنشاء كلمة مرور مشفرة
password = "mypassword123"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# إنشاء مستخدم جديد
success = DatabaseLayer.UserManager.CreateUser(
    student_id="27123456",  # رقم الطالب
    email="ahmed@example.com",
    password_hash=password_hash,
    role="student",
    display_name="أحمد محمد",
    mobile="0501234567"
)

if success:
    print("✅ تم إنشاء المستخدم بنجاح!")
else:
    print("❌ فشل في إنشاء المستخدم")
```

### مثال 8: المصادقة على المستخدم

```python
from DATABASE_LAYER import DatabaseLayer
import bcrypt

# بيانات تسجيل الدخول
email = "ahmed@example.com"
password = "mypassword123"

# تشفير كلمة المرور للمقارنة
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# المصادقة
user = DatabaseLayer.UserManager.AuthenticateUser(email, password_hash)

if user:
    print(f"✅ مرحباً {user['display_name']}!")
    print(f"دورك: {user['role']}")
else:
    print("❌ بيانات تسجيل الدخول غير صحيحة")
```

## 🔧 نصائح مهمة للمبتدئين

### 1. استيراد الملف
```python
from DATABASE_LAYER import DatabaseLayer
```

### 2. فهم أنواع البيانات المُعادة
- `AddStudent()` ترجع `bool` (True/False)
- `GetStudent()` ترجع `Dict` أو `None`
- `GetAllStudents()` ترجع `List[Dict]`

### 3. التحقق من النتائج دائماً
```python
result = DatabaseLayer.StudentManager.AddStudent(...)
if result:
    print("نجح!")
else:
    print("فشل!")
```

### 4. استخدام try/except للتعامل مع الأخطاء
```python
try:
    success = DatabaseLayer.CourseManager.AddCourse(...)
    if success:
        print("تم بنجاح!")
except Exception as e:
    print(f"حدث خطأ: {e}")
```

## 📚 مصطلحات مهمة

- **Primary Key**: مفتاح أساسي (معرف فريد لكل صف)
- **Foreign Key**: مفتاح خارجي (ربط بين الجداول)
- **CRUD**: Create, Read, Update, Delete (الإنشاء، القراءة، التحديث، الحذف)
- **Transaction**: عملية قاعدة بيانات (تُحفظ أو تُلغى كلها)
- **Connection**: الاتصال بقاعدة البيانات
- **Cursor**: مؤشر لتنفيذ الأوامر على قاعدة البيانات

## 🎯 أفضل الممارسات

1. **أغلق الاتصالات دائماً**: الملف يتولى هذا تلقائياً
2. **تحقق من البيانات**: تأكد من صحة البيانات قبل الحفظ
3. **استخدم try/except**: للتعامل مع الأخطاء
4. **لا تكرر الكود**: استخدم الدوال الجاهزة
5. **أسماء واضحة**: استخدم أسماء متغيرات واضحة

## 🚨 ملاحظات مهمة

- قاعدة البيانات تُنشأ تلقائياً عند استيراد الملف لأول مرة
- جميع الدوال آمنة ولا تحتاج لإغلاق اتصالات يدوياً
- البيانات تُحفظ فوراً عند استدعاء `commit()`
- في حالة خطأ، يتم إلغاء العملية تلقائياً

## 📞 للمساعدة

إذا واجهت أي مشكلة:
1. تحقق من رسائل الخطأ
2. تأكد من صحة البيانات المُرسلة
3. راجع أمثلة الاستخدام أعلاه
4. جرب تشغيل الكود خطوة بخطوة

**نصيحة**: ابدأ بقراءة الكود وفهم كل دالة قبل استخدامها!
