import re

with open('backend/app.py', 'r') as f:
    content = f.read()

# Fix the setup_database syntax
pattern = r'def setup_database\(app\):.*?except Exception as e:\n            print\(f"❌ Error setting up database: \{e\}"\)'

fixed = """def setup_database(app):
    \"\"\"Initialize the database and create sample data if empty\"\"\"
    with app.app_context():
        try:
            db.create_all()
            from models import User
            if not User.query.first():
                print("Creating sample data...")
                create_sample_data()
                print("✅ Sample data created successfully!")
            else:
                print("✅ Database already has sample data")
        except Exception as e:
            print(f"❌ Error setting up database: {e}")"""

content = re.sub(pattern, fixed, content, flags=re.DOTALL)

with open('backend/app.py', 'w') as f:
    f.write(content)
