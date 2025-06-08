# Django Todo Application

A feature-rich todo application built with Django and Django REST Framework. This application allows users to manage their tasks with categories, priorities, and filtering capabilities.

## Features

- User Authentication (Register/Login)
- Create, Read, Update, and Delete todos
- Categorize todos (Study, Work, Personal, etc.)
- Priority levels (Low, Medium, High)
- Filter todos by:
  - Status (All/Active/Completed)
  - Priority (All/High/Medium/Low)
  - Category
- Custom category creation
- RESTful API endpoints
- Responsive UI with Bootstrap

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository or download the source code:
```powershell
git clone <repository-url>
cd todo_django
```

2. Create a virtual environment:
```powershell
python -m venv .env
```

3. Activate the virtual environment:
```powershell
.\.env\Scripts\activate
```

4. Install the required packages:
```powershell
pip install django djangorestframework django-filter django-cors-headers
```

5. Apply database migrations:
```powershell
python manage.py migrate
```

6. Create a superuser (admin):
```powershell
python manage.py createsuperuser
```

## Running the Application

1. Start the development server:
```powershell
python manage.py runserver
```

2. Open your web browser and navigate to:
- Main application: http://127.0.0.1:8000/


## Usage

1. Register a new account or login with existing credentials
2. Create todos:
   - Enter todo title and description
   - Select priority level
   - Choose or create a category
3. Filter todos using the buttons:
   - All/Active/Completed
   - Priority levels
   - Categories
4. Manage todos:
   - Mark as complete/incomplete
   - Edit details
   - Delete tasks

## API Endpoints

- List/Create todos: `GET/POST /api/todos/`
- Retrieve/Update/Delete todo: `GET/PUT/DELETE /api/todos/{id}/`
- Filter parameters:
  - `?completed=true/false`
  - `?priority=1/2/3`
  - `?category={id}`

## Project Structure

```
todo_django/
├── todo_project/       # Main project directory
│   ├── settings.py     # Project settings
│   └── urls.py        # Main URL configuration
├── todo_app/          # Todo application
│   ├── models.py      # Data models
│   ├── views.py       # View logic
│   ├── serializers.py # API serializers
│   ├── urls.py        # App URL configuration
│   └── templates/     # HTML templates
└── manage.py          # Django management script
```

## Technologies Used

- Django 5.2.1
- Django REST Framework
- Bootstrap 5
- SQLite database
- HTML/CSS/JavaScript

## Security Notes

1. Change the `SECRET_KEY` in settings.py before deployment
2. Set `DEBUG = False` in production
3. Update `ALLOWED_HOSTS` with your domain
4. Use environment variables for sensitive information
5. Configure CORS settings appropriately

## Contributing

Feel free to submit issues and enhancement requests!
