import re

with open('backend/app.py', 'r') as f:
    content = f.read()

setup_func_new = """def setup_database(app):
    \"\"\"Initialize the database and create sample data if empty\"\"\"
    with app.app_context():
        db.create_all()
        # Check if database is empty by looking for users
        from models import User
        if not User.query.first():
            print("Creating sample data...")
            create_sample_data()
            print("✅ Sample data created successfully!")
"""

content = re.sub(r'def setup_database.*?print\("✅ Sample data created successfully!"\)', setup_func_new, content, flags=re.DOTALL)

with open('backend/app.py', 'w') as f:
    f.write(content)
print("Updated setup_database()")
