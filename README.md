# Disaster Management & Relief Coordination System

A centralized, full-fledged disaster relief coordination platform designed to streamline crisis response. It features real-time resource inventory tracking, dynamic event mapping, secure donation workflows, and an advanced, role-based task delegation system for volunteers and administrators.

---

## 🌟 Key Features

### 🏢 Role-Based Ecosystem
- **Administrators**: Full system oversight. Admins can add resources, approve/reject relief requests, and manually assign tasks to specific volunteers through the dedicated Volunteer Management dashboard.
- **Users**: Affected individuals can browse active disaster events, request specific relief resources, and track the live delivery status of their requests.
- **Volunteers**: A dedicated workspace for users who sign up to help. Volunteers can accept open tasks, manage their active assignments, and update delivery statuses (e.g., In Progress, Completed).

### 📦 Resource & Inventory Management
- Real-time tracking of relief resources (Food, Medical, Shelter, Tools).
- Automated inventory deduction and transactional integrity handled safely via pure Python SQLAlchemy (SQLite-compatible).
- Double-entry prevention for secure donation processing.

### 🔒 Enterprise-Grade Security & UX
- Global CSRF (Cross-Site Request Forgery) protection implemented across all form submissions.
- Flash message system providing users with immediate, friendly UI feedback (success/error banners) instead of raw JSON dumps.
- Highly resilient dynamic routing using Flask's `url_for()`.

### 🗺️ Interactive Disaster Mapping
- Visualize active disaster events and their severity (Critical, High, Medium) on a dynamic, interactive map powered by **Leaflet.js** and **OpenStreetMap**.

### 🧪 Automated Testing
- Comprehensive `pytest` suite ensuring all core workflows (authentication, user requests, admin approvals) function exactly as expected.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, SQLAlchemy, Flask-Login, Flask-WTF, Gunicorn
- **Database**: SQLite (No external DB server required; zero-configuration)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2 Templates
- **Mapping**: Leaflet.js

---

## 🚀 Local Development (Getting Started)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Disaster Management & Relief Coordination System"
cd backend
```

### 2. Set Up the Environment
It is highly recommended to use a virtual environment.
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
python app.py
```
*Note: On its first run, the system will automatically generate a fresh SQLite database (`disaster.db`) populated with sample events, resources, users, and tasks so you can test the UI immediately.*

### 4. Access the App
Open your browser and navigate to: **http://localhost:5001**

---

## ☁️ Cloud Deployment (Render.com)

This project is fully pre-configured to be deployed securely and reliably for free on [Render](https://render.com/).

1. Log into Render and create a new **Web Service**.
2. Connect your GitHub repository.
3. Use the following deployment configuration:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn "app:create_app()"`
4. Under **Advanced**, add the following settings to ensure your SQLite database is permanent and never wiped:
   - **Add Environment Variable** -> Key: `RENDER`, Value: `true`
   - **Add Disk** -> Name: `database`, Mount Path: `/var/data`, Size: `1 GB`
5. Click **Create Web Service**. Your app is now live!

---

## 🔑 Demo Accounts

To immediately test the role-based features locally or on your deployed site, use the automatically generated sample accounts:

**Admin Account**
- **Email**: `admin@disaster.org`
- **Password**: `password123`

**Regular User / Volunteer Account**
- **Email**: `john@example.com`
- **Password**: `password123`

---

## 🧪 Running Tests
To verify the integrity of the application routing and user roles, run the automated test suite:
```bash
cd backend
source venv/bin/activate
pytest ../tests/
```
