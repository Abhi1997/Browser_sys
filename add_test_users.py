from authentication import Authentication

# Initialize authentication
auth = Authentication(host="localhost", user="root", password="Innovation", database="edubrowser")

# Test users with different roles
test_users = [
    {"username": "superadmin1", "password": "super123!", "role": "superadmin"},
    {"username": "admin1", "password": "admin123!", "role": "admin"},
    {"username": "admin2", "password": "admin456!", "role": "admin"},
    {"username": "teacher1", "password": "teach123!", "role": "teacher"},
    {"username": "teacher2", "password": "teach456!", "role": "teacher"},
    {"username": "teacher3", "password": "teach789!", "role": "teacher"},
    {"username": "student1", "password": "student123!", "role": "student"},
    {"username": "student2", "password": "student456!", "role": "student"},
    {"username": "student3", "password": "student789!", "role": "student"},
    {"username": "student4", "password": "student012!", "role": "student"},
]

# Save credentials to file
with open("test_users_credentials.txt", "w") as f:
    f.write("=" * 60 + "\n")
    f.write("TEST USER CREDENTIALS FOR EDUBROWSER\n")
    f.write("=" * 60 + "\n\n")
    
    for user in test_users:
        f.write(f"Username: {user['username']:<15} | Password: {user['password']:<15} | Role: {user['role']}\n")
    
    f.write("\n" + "=" * 60 + "\n")
    f.write("Use these credentials to login to the browser application\n")
    f.write("=" * 60 + "\n")

print("Credentials saved to test_users_credentials.txt")

# Register users in database
print("\nAdding users to database...")
success_count = 0
for user in test_users:
    try:
        result = auth.register_user(
            username=user["username"],
            password=user["password"],
            role=user["role"]
        )
        if result:
            print(f"✓ Created: {user['username']} ({user['role']})")
            success_count += 1
        else:
            print(f"✗ Failed: {user['username']} - may already exist")
    except Exception as e:
        print(f"✗ Error creating {user['username']}: {e}")

print(f"\n{success_count}/{len(test_users)} users created successfully!")
print(f"\nCredentials have been saved to: test_users_credentials.txt")
