# 3D4P - Prosthetics for Palestine 🦾

A humanitarian Django web application connecting individuals in need of prosthetic limbs with compassionate donors worldwide. This platform specifically serves those affected by conflict, providing a secure and moderated environment for medical assistance requests.

## 🌟 Features

### Core Functionality
- **User Authentication & Verification**: Secure signup/login with member verification system
- **Post Management**: Create regular posts and donation requests with AI moderation
- **File Upload Support**: Medical files (DICOM, NIfTI), documents, and images
- **AI Content Moderation**: OpenAI integration for text moderation and NudeNet for image safety
- **Admin Dashboard**: Comprehensive management interface for administrators
- **Donation System**: Integrated Stripe payment processing
- **Responsive Design**: Mobile-friendly Bootstrap interface

### Security Features
- **Environment Variable Configuration**: All secrets externalized
- **HTTPS Security Headers**: HSTS, CSP, XSS protection
- **File Upload Validation**: Content type checking and size limits
- **PostgreSQL Database**: Production-ready database backend
- **Custom Error Handling**: Secure error pages with logging
- **Security Middleware**: Suspicious activity detection and logging

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Node.js (for frontend assets)
- OpenAI API key
- Stripe account (for payments)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd prosthetic_3D4P
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database Setup**
```bash
# Create PostgreSQL database
createdb prosthetic_3d4p

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

6. **Static Files**
```bash
python manage.py collectstatic
```

7. **Run Development Server**
```bash
python manage.py runserver
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Security
SECRET_KEY=your-django-secret-key
DEBUG=False

# Database
DB_NAME=prosthetic_3d4p
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_app_password

# API Keys
OPENAI_API_KEY=your-openai-api-key-here

# Stripe
STRIPE_PUBLIC_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

# Deployment
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Medical File Support

The platform supports various medical file formats:
- **DICOM** (.dcm) - Medical imaging standard
- **NIfTI** (.nii, .nii.gz) - Neuroimaging format
- **HL7** (.hl7) - Healthcare messaging standard
- **Medical Reports** (.pdf, .doc, .docx, .xml)
- **Data Exports** (.csv, .xlsx, .xls)

## 🏗️ Architecture

### Project Structure
```
prosthetic_3D4P/
├── admin_dashboard/     # Admin interface
├── campaigns/          # Campaign management
├── donations/          # Payment processing
├── posts/             # Content management
├── users/             # User authentication
├── verification/      # Member verification
├── utils/             # Shared utilities
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── media/            # Uploaded files
└── logs/             # Application logs
```

### Database Models
- **CustomUser**: Extended user model with verification status
- **Post**: Content posts with moderation
- **DonationRequest**: Prosthetic assistance requests
- **MemberProfile**: User profile information
- **MemberApplication**: Verification applications

## 🔒 Security Considerations

### Implemented Security Measures
1. **Environment Variables**: All secrets externalized
2. **HTTPS Enforcement**: SSL redirect and HSTS headers
3. **File Upload Security**: Type validation and size limits
4. **Content Moderation**: AI-powered text and image filtering
5. **Error Handling**: Custom error pages without information leakage
6. **Logging**: Comprehensive security event logging
7. **Database Security**: PostgreSQL with proper authentication

### Additional Recommendations
1. **SSL Certificate**: Use Let's Encrypt or commercial SSL
2. **Firewall**: Configure server firewall rules
3. **Backups**: Regular database and media backups
4. **Monitoring**: Implement uptime and security monitoring
5. **Updates**: Regular dependency updates

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up SSL certificate
- [ ] Configure PostgreSQL
- [ ] Set up email service
- [ ] Configure static file serving
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Docker Deployment (Optional)
```dockerfile
# Dockerfile included for containerized deployment
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "prosthetic_3D4P.wsgi:application"]
```

## 📊 Monitoring

### Logging
- Application logs: `logs/django.log`
- Security logs: `logs/security.log`
- Error tracking with detailed stack traces
- Suspicious activity monitoring

### Health Checks
- Database connectivity
- External API availability
- File upload functionality
- Email service status

## 🤝 Contributing(Check CONTRIBUTING.md for full details)

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Include error handling
- Write unit tests

## 📱 API Documentation

### Authentication Endpoints
- `POST /users/signup/` - User registration
- `POST /users/login/` - User login
- `POST /users/logout/` - User logout

### Content Endpoints
- `GET /posts/` - List all posts
- `POST /posts/create/` - Create new post
- `GET /posts/<id>/` - Get specific post
- `POST /donations/` - Create donation request

## 🛠️ Maintenance

### Regular Tasks
- Monitor log files for errors
- Update dependencies monthly
- Backup database weekly
- Review security logs
- Update SSL certificates

### Performance Optimization
- Enable database query optimization
- Configure Redis for caching
- Optimize image processing
- Monitor response times

## 📞 Support

For technical support or questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 📄 License

This project is created for humanitarian purposes. Please use responsibly.

---

**Made with ❤️ for humanity - Connecting hope with healing**