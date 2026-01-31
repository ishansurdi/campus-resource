# CAMPUSPHERE - Campus Resource Management System

A comprehensive Django REST Framework-based campus management system with event management, club administration, approval workflows, and expense tracking.

## 🚀 Features

- **Two-Tier Approval System**: Faculty → Admin approval workflow for events and club applications
- **Club Management**: Register clubs, manage members, assign faculty mentors
- **Event Management**: Create, approve, and manage campus events with full lifecycle tracking
- **Expense Ledger**: Track event expenses with live budget monitoring and utilization
- **User Roles**: Admin, Faculty, Student with role-based access control
- **Authentication**: JWT-based authentication with club-based login
- **Event Registration**: Students can register for events with capacity management
- **Certificates & Attendance**: Track attendance and generate certificates
- **Resource Booking**: (In development) Book campus resources like halls, equipment

## 📋 Tech Stack

### Backend
- **Framework**: Django 5.0+ with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **API Documentation**: RESTful API with comprehensive endpoints

### Frontend
- **Framework**: Vanilla JavaScript (No framework dependencies)
- **CSS**: Tailwind CSS 4
- **Architecture**: Multi-page application with role-based dashboards

## 🗂️ Project Structure

```
campusresource/
├── backend/                    # Django backend
│   ├── authentication/         # Main app with models, views, URLs
│   │   ├── models.py          # Event, Club, ClubMember, EventExpense models
│   │   ├── views.py           # Authentication & club views
│   │   ├── event_views.py     # Event management views
│   │   ├── application_views.py # Application approval views
│   │   ├── serializers.py     # DRF serializers
│   │   └── urls.py            # API routes
│   ├── campusphere/           # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── requirements.txt       # Python dependencies
│
└── frontend/                  # Static frontend
    ├── index.html             # Landing page
    ├── login.html             # Login page with club selection
    ├── auth.js                # Authentication utilities
    └── dashboards/
        ├── admin-dashboard.html
        ├── approvals.html     # Admin approvals interface
        ├── faculty-dashboard/
        │   └── faculty-dashboard.html
        └── student-dashboard/
            ├── student-dashboard.html
            ├── events.html    # Browse & register for events
            ├── event-ledger.html # Expense tracking
            ├── applications.html # Submit event applications
            ├── clubs.html     # Join clubs
            └── profile.html
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- pip (Python package manager)

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/ishansurdi/campus-resource.git
cd campus-resource
```

2. **Set up Python virtual environment**
```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Database**

Create a PostgreSQL database and update `backend/campusphere/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Or use environment variables (recommended for production):

```bash
# Create .env file in backend/
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Backend API: http://localhost:8000/api/
- Frontend: Open `frontend/index.html` in browser (or use a local server)

### Using a Local Web Server for Frontend

```bash
# Using Python
cd frontend
python -m http.server 3000

# Or using Node.js
npx http-server -p 3000
```

Then access: http://localhost:3000

## 🚀 Deployment on Render

### Step 1: Prepare for Deployment

1. **Create `render.yaml` in project root** (already included)

2. **Update `backend/campusphere/settings.py`**:
   - Set `DEBUG = False` in production
   - Configure `ALLOWED_HOSTS`
   - Set up `STATIC_ROOT` and `STATICFILES_DIRS`
   - Configure database using environment variables

3. **Ensure `requirements.txt` is up to date**:
```bash
pip freeze > requirements.txt
```

### Step 2: Deploy on Render

1. **Push code to GitHub**
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

2. **Create PostgreSQL Database on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "PostgreSQL"
   - Name: `campusphere-db`
   - Region: Choose nearest
   - Plan: Free or Starter
   - Copy the Internal Database URL

3. **Create Web Service on Render**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `campusphere`
     - **Region**: Same as database
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
     - **Start Command**: `gunicorn campusphere.wsgi:application`

4. **Set Environment Variables**
   - `DATABASE_URL`: (Auto-added when you link database)
   - `SECRET_KEY`: Generate a new one: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
   - `PYTHON_VERSION`: `3.11.0`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment
   - Access your app at: `https://your-app-name.onrender.com`

### Step 3: Deploy Frontend (Static Site)

1. **Create Static Site on Render**
   - Click "New +" → "Static Site"
   - Connect same repository
   - Configure:
     - **Name**: `campusphere-frontend`
     - **Root Directory**: `frontend`
     - **Build Command**: (leave empty)
     - **Publish Directory**: `.`

2. **Update API URLs in Frontend**
   - Update all `http://localhost:8000` to your Render backend URL in:
     - `auth.js`
     - All HTML files with fetch calls

3. **Deploy and Access**
   - Your frontend will be at: `https://campusphere-frontend.onrender.com`

## 🔐 Environment Variables

Required environment variables for production:

```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS (if frontend on different domain)
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# Optional
DJANGO_SETTINGS_MODULE=campusphere.settings
PYTHON_VERSION=3.11.0
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/login/` - Login with email/password/club
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/logout/` - Logout user
- `GET /api/auth/clubs/` - Get all clubs (public)

### Event Endpoints
- `GET /api/auth/events/` - List all events
- `GET /api/auth/events/{id}/` - Event details
- `POST /api/auth/event-applications/` - Submit event application
- `GET /api/auth/event-applications/pending-faculty/` - Faculty pending approvals
- `POST /api/auth/event-applications/{id}/faculty-approve/` - Faculty approve
- `GET /api/auth/event-applications/pending-admin/` - Admin pending approvals
- `POST /api/auth/event-applications/{id}/admin-approve/` - Admin approve

### Expense Endpoints
- `GET /api/auth/events/{id}/expenses/` - List event expenses
- `POST /api/auth/events/{id}/expenses/` - Add expense

### Club Endpoints
- `GET /api/auth/clubs/` - List clubs
- `POST /api/auth/clubs/join/` - Join a club
- `GET /api/auth/my-clubs/` - User's clubs

## 👥 User Roles & Permissions

### Admin
- Approve/reject all events and club applications
- Manage clubs and users
- View all expenses and budgets
- Access admin dashboard

### Faculty
- Approve/reject events from their clubs
- View club member applications
- Access faculty dashboard
- Mentor assigned clubs

### Student
- Submit event applications
- Join clubs
- Register for events
- Track expenses for their events
- View event ledger

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Create test data
python manage.py loaddata fixtures/sample_data.json
```

## 🔒 Security Features

- JWT token authentication
- CSRF protection
- Role-based access control
- Password hashing with Django's built-in system
- SQL injection protection (Django ORM)
- XSS protection

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Developer

**Ishan Surdi**
- GitHub: [@ishansurdi](https://github.com/ishansurdi)
- Repository: [campus-resource](https://github.com/ishansurdi/campus-resource)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Contact: [Your contact information]

## 🗺️ Roadmap

- [ ] OCR for expense receipts
- [ ] Mobile responsive design improvements
- [ ] Email notifications
- [ ] Analytics dashboard
- [ ] Resource booking system
- [ ] Event calendar view
- [ ] Export reports (PDF/Excel)
- [ ] Multi-language support

---

**Note**: This is an active development project. Features and documentation are updated regularly.
