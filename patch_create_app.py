import re

with open('backend/app.py', 'r') as f:
    content = f.read()

# Add setup_database inside create_app
setup_injection = """
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(volunteer_bp, url_prefix='/volunteer')

    # Automatically set up the database and sample data if not exists
    with app.app_context():
        setup_database(app)

    return app
"""

content = re.sub(r'    # Register blueprints.*return app', setup_injection, content, flags=re.DOTALL)

with open('backend/app.py', 'w') as f:
    f.write(content)
print("Updated create_app() to run setup_database()")
