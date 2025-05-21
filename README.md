# LearnMore: Interactive Learning Platform

LearnMore is a SaaS learning platform designed to create and manage interactive online courses with AI tutor integration.


## 🚀 Features

- **Course Management**: Create, edit, and manage interactive courses
- **Course Catalog**: Browse courses with pagination, filtering, and search functionality
- **AI Tutor Integration**: OpenAI-powered AI tutoring for personalized learning assistance
- **User Authentication**: Secure registration and login system with role-based access control
- **Responsive Design**: Mobile-friendly interface for learning on any device
- **QR Code Sharing**: Easy sharing of course links via QR codes

## 🛠️ Technologies

- **Backend**: Django 4.2+
- **Database**: SQLite (development), PostgreSQL (production)
- **AI Integration**: OpenAI API
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Deployment**: Gunicorn, Nginx

## 📋 Requirements

- Python 3.9+
- Django 4.2+
- OpenAI API key (for AI tutor functionality)
- Additional dependencies listed in `requirements.txt`

## 🔧 Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd learnmore
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r learnmore/requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with:
   ```
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Run migrations**
   ```bash
   cd learnmore
   python manage.py migrate
   ```

6. **Seed initial data (optional)**
   ```bash
   python manage.py seed_courses
   ```
   >> Note that seeding courses creates 3 test users, `admin`, `instructor` and `student` with passwords set as per the script.

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Web Interface: http://127.0.0.1:8000/
   - Admin Interface: http://127.0.0.1:8000/admin/

## 🚀 Deployment

### Prerequisites
- A server with Python 3.9+ installed
- Nginx web server
- Gunicorn WSGI server
- PostgreSQL database (recommended for production)

### Deployment Steps

1. **Set up the server environment**
   - Install required packages:
     ```bash
     sudo apt update
     sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib
     ```

2. **Clone the repository on the server**
   ```bash
   git clone <repository-url>
   cd learnmore
   ```

3. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r learnmore/requirements.txt
   pip install gunicorn
   ```

5. **Configure production settings**
   - Update `settings.py` for production:
     - Set `DEBUG = False`
     - Update `ALLOWED_HOSTS`
     - Configure database settings for PostgreSQL
     - Set up static files handling

6. **Set up environment variables**
   Create a `.env` file with production values:
   ```
   SECRET_KEY=your_production_secret_key
   DEBUG=False
   ALLOWED_HOSTS=your_domain.com
   DATABASE_URL=postgres://user:password@localhost/dbname
   OPENAI_API_KEY=your_openai_api_key
   ```

7. **Set up the database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
   ```

8. **Configure Gunicorn**
   - Use the provided `gunicorn_config.py` and `learnmore.service` files
   - Enable and start the service:
     ```bash
     sudo cp learnmore.service /etc/systemd/system/
     sudo systemctl enable learnmore
     sudo systemctl start learnmore
     ```

9. **Configure Nginx**
   - Create a new configuration in `/etc/nginx/sites-available/learnmore`:
     ```nginx
     server {
         listen 80;
         server_name your_domain.com;

         location = /favicon.ico { access_log off; log_not_found off; }
         
         location /static/ {
             root /path/to/learnmore;
         }

         location / {
             include proxy_params;
             proxy_pass http://unix:/run/gunicorn.sock;
         }
     }
     ```
   - Enable the site:
     ```bash
     sudo ln -s /etc/nginx/sites-available/learnmore /etc/nginx/sites-enabled
     sudo nginx -t
     sudo systemctl restart nginx
     ```

10. **Set up SSL with Let's Encrypt (optional but recommended)**
    ```bash
    sudo apt install certbot python3-certbot-nginx
    sudo certbot --nginx -d your_domain.com
    ```

## 🔧 AI Tutor Setup

The AI Tutor feature requires an OpenAI API key:

1. Obtain an API key from [OpenAI](https://platform.openai.com/)
2. Add the key to your environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```
3. The AI tutor automatically ingests course content when courses are created using the `seed_courses` command
4. Students can access the AI tutor from their course pages

## 📊 Admin Interface

Access the admin interface at `/admin/` to:
- Manage user accounts
- Create and edit courses
- Monitor subscription information
- View and manage student progress

## 🔄 Testing Accounts

For demonstration purposes, the following test accounts are available (after running migrations and seeding data):

- **Admin**: admin@learnmore.com / adminpassword
- **Instructor**: instructor@learnmore.com / instructorpassword
- **Student**: student@learnmore.com / studentpassword

## 📝 License

[MIT](LICENSE)

## 👥 Contributors

- [Your Name](mailto:your.email@example.com) 