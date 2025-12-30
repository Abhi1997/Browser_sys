from authentication import Authentication

auth = Authentication(host="localhost", user="root", password="Innovation", database="edubrowser")
auth.register_user("admin", "admin1234", "admin")
print("Admin user created successfully!")