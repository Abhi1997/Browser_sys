from authentication import Authentication

auth = Authentication(host="localhost", user="root", password="Innovation", database="edubrowser")
auth.register_user("admin", "admin123", "super-admin")
print("Admin user created successfully!")