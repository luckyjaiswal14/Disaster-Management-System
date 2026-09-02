# Disaster Management & Relief Coordination System 🌍

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000.svg?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg?style=flat-square&logo=sqlite)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3.svg?style=flat-square&logo=bootstrap)](https://getbootstrap.com/)
[![PythonAnywhere](https://img.shields.io/badge/PythonAnywhere-Deployable-black.svg?style=flat-square&logo=python)](https://www.pythonanywhere.com/)

**Disaster Management & Relief Coordination System** is a production-grade, highly intuitive crisis response platform. Built with Python and Flask, it leverages real-time interactive mapping (Leaflet.js) to visualize active disasters and utilizes an advanced role-based state machine to coordinate volunteers, approve resource requests, and manage emergency inventories securely with pure Python SQLAlchemy.

---

## 🌟 Key Capabilities

- **Interactive Disaster Mapping**: Hardware-accelerated mapping powered by Leaflet.js and OpenStreetMap to dynamically plot disaster events and severity levels visually.
- **Advanced Volunteer Routing**: A complex, role-based task delegation engine that allows Administrators to assign relief tasks to specific volunteers, and tracks real-time fulfillment states.
- **Automated Inventory Management**: Intelligent double-entry prevention and transactional database logic that safely deducts from relief inventories as soon as requests are approved or donations are made.
- **Enterprise-Grade Security**: Global Cross-Site Request Forgery (CSRF) protection implemented across all endpoints via Flask-WTF to ensure military-grade request integrity.
- **Comprehensive Feedback Loops**: Real-time Jinja2 UI rendering and Flash messaging providing users with instantaneous, friendly UI feedback during high-stress usage.

---

## 💻 Tech Stack

- **Backend Logic**: Python 3, Flask (API & Template Routing), Gunicorn
- **Database Engine**: SQLite, SQLAlchemy ORM, Alembic (Migrations)
- **Security**: Flask-Login, Flask-WTF (CSRF Protection), Werkzeug Security
- **Frontend UI**: HTML5, CSS3, Bootstrap 5, FontAwesome
- **Mapping Visualization**: Leaflet.js, OpenStreetMap
- **Deployment**: PythonAnywhere (Persistent Cloud Filesystem)

---

## 🏗️ Architecture

```text
                                  ┌──────────────────┐
                                  │     GitHub       │
                                  │    Repository    │
                                  └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │  PythonAnywhere  │
                                  │                  │
                                  │ Persistent Disk  │
                                  └────────┬─────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
          ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
          │      Flask      │   │   SQLAlchemy     │   │     Leaflet     │
          │                 │   │                  │   │                 │
          │ Routing Logic   │   │ Inventory Math   │   │ Event Mapping   │
          │ Request Parsing │◄──┤ User Profiles    │──►│ Lat/Lng Data    │
          │ Template Render │   │ Volunteer State  │   │ Severity Layers │
          │ API Endpoints   │   │ SQLite Engine    │   │ Popup Modals    │
          └────────┬────────┘   └──────────────────┘   └─────────────────┘
                   │
       ┌───────────┼─────────────────────────────────┐
       │           │                │                │
       ▼           ▼                ▼                ▼
  Jinja2 UI    Bootstrap 5    CSRF Security      Form Inputs
```

---

## 📂 Project Structure

```text
Disaster-Management-System/
├── backend/
│   ├── routes/               # Blueprint routing (admin, auth, user, volunteer)
│   ├── templates/            # HTML Jinja2 templates (Dashboards & Auth)
│   ├── app.py                # Main Flask application and server initialization
│   ├── config.py             # Environment & deployment configurations
│   ├── extensions.py         # SQLAlchemy and Flask extension singletons
│   ├── models.py             # Database schemas and relationships
│   └── requirements.txt      # Python dependencies
├── tests/                    # Comprehensive Pytest automated testing suite
└── README.md                 # Project documentation
```

The application uses a persistent `disaster.db` generated on startup via `app.py`. The initialization script automatically seeds the database with administrative accounts, active emergency events, and sample inventory resources.

---

## 🚀 Deployment Guide

### Option 1: Deploy to PythonAnywhere (Recommended Free Tier)

This platform is pre-configured for deployment on PythonAnywhere, ensuring your SQLite database remains permanent and secure.

#### Steps:
1. **Create an account on [PythonAnywhere](https://www.pythonanywhere.com/).**
2. **Open a Bash Console** and clone the repository:
   ```bash
   git clone https://github.com/luckyjaiswal14/Disaster-Management-System.git
   mkvirtualenv --python=/usr/bin/python3.10 venv
   cd Disaster-Management-System/backend
   pip install -r requirements.txt
   ```
3. **Configure the Web App**: Go to the **Web** tab, click **Add a new web app**, and select **Manual Configuration** -> **Python 3.10**.
4. **Set Paths**:
   - **Virtualenv**: `/home/yourusername/.virtualenvs/venv`
   - **WSGI configuration file**: Replace its contents with:
     ```python
     import sys
     import os

     project_home = '/home/yourusername/Disaster-Management-System/backend'
     if project_home not in sys.path:
         sys.path = [project_home] + sys.path

     from app import create_app
     application = create_app()
     ```
5. Click **Reload**. Your application is now live globally!

### Option 2: Run Locally (Python)

#### Prerequisites:
- Python 3.9+
- pip (Python package manager)

#### Installation & Setup:
```bash
# 1. Clone the repository
git clone https://github.com/luckyjaiswal14/Disaster-Management-System.git
cd Disaster-Management-System/backend

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

#### Launch the Platform:
```bash
python app.py
```
The application will launch automatically on `http://localhost:5001`.

---

## 🛡️ Design Standard

Every component in this project fulfills three critical constraints:
1. **Performance**: Database transactions via SQLAlchemy execute instantly, ensuring real-time inventory deductions without race conditions.
2. **Security**: Role-based access control (RBAC) strictly prevents unauthorized users from modifying relief data, while CSRF tokens protect all state-changing endpoints.
3. **Data Integrity**: The volunteer state machine flawlessly handles complex task assignment lifecycles (Pending -> Accepted -> In Progress -> Fulfilled) without data orphanization.

---

## 📄 License

MIT License - Copyright 2026.
