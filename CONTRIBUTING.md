# Contributing to 3D4P - Prosthetics for Palestine

Thank you for your interest in contributing to this humanitarian project! Every contribution helps connect people in need with life-changing prosthetic assistance.

## 🤝 How to Contribute

### Types of Contributions Welcome
- 🐛 Bug fixes and security improvements
- ✨ New features (medical file support, accessibility features)
- 📚 Documentation improvements
- 🌍 Translations and internationalization
- 🎨 UI/UX enhancements
- 🧪 Testing and quality assurance
- 📱 Mobile responsiveness improvements

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git
- Basic Django knowledge
- Understanding of humanitarian/medical contexts

### Development Setup

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/prosthetic_3D4P.git
   cd prosthetic_3D4P
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   
   # Install dependencies
   pip install -r requirements-dev.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with development settings
   ```

4. **Set Up Database**
   ```bash
   python manage.py migrate --settings=prosthetic_3D4P.settings_local
   python manage.py createsuperuser --settings=prosthetic_3D4P.settings_local
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver --settings=prosthetic_3D4P.settings_local
   ```

## 📋 Contribution Process

### 1. Find or Create an Issue
- Check [existing issues](https://github.com/YOUR_USERNAME/prosthetic_3D4P/issues)
- Look for issues labeled `good-first-issue` or `help-wanted`
- Create new issue for bugs/features with detailed description

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### 3. Make Your Changes
- Follow our coding standards (see below)
- Write tests for new features
- Update documentation as needed
- Ensure security best practices

### 4. Test Your Changes
```bash
# Run tests
python manage.py test --settings=prosthetic_3D4P.settings_local

# Check for security issues
python manage.py check --deploy --settings=prosthetic_3D4P.settings_local

# Test file uploads and AI moderation (if applicable)
```

### 5. Commit Your Changes
```bash
git add .
git commit -m "feat: add medical file validation for DICOM format"
# Use conventional commit format:
# feat: new feature
# fix: bug fix
# docs: documentation
# test: testing
# refactor: code refactoring
# security: security improvements
```

### 6. Push and Create Pull Request
```bash
git push origin your-branch-name
```
Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/videos for UI changes
- Testing instructions

## 🎯 Coding Standards

### Python/Django Guidelines
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Handle errors gracefully
- Validate all user inputs

### Security Requirements
- Never commit secrets or API keys
- Validate all file uploads
- Sanitize user inputs
- Follow OWASP security guidelines
- Test for SQL injection and XSS

### Medical/Humanitarian Context
- Be sensitive to medical terminology
- Support international users (i18n)
- Consider accessibility requirements
- Respect user privacy and data protection

## 🔍 Code Review Process

### What We Look For
1. **Functionality** - Does it work as intended?
2. **Security** - No vulnerabilities introduced?
3. **Code Quality** - Clean, readable, maintainable?
4. **Testing** - Adequate test coverage?
5. **Documentation** - Clear comments and docs?
6. **Humanitarian Impact** - Does it help our mission?

### Review Timeline
- Initial review: 2-3 business days
- Follow-up reviews: 1-2 business days
- Maintainer approval required for merge

## 🌍 Special Considerations

### Medical File Handling
- Understand DICOM, NIfTI, HL7 formats
- Ensure HIPAA-like privacy protection
- Test with real medical file samples (anonymized)

### Internationalization
- Support RTL languages (Arabic, Hebrew)
- Use Django's i18n framework
- Consider cultural sensitivities

### Accessibility
- Follow WCAG 2.1 guidelines
- Test with screen readers
- Ensure keyboard navigation

## 🐛 Reporting Issues

### Bug Reports
Include:
- Steps to reproduce
- Expected vs actual behavior
- Browser/OS information
- Screenshots/error messages
- Security impact (if applicable)

### Feature Requests
Include:
- Problem you're solving
- Proposed solution
- User impact
- Technical considerations

## 📞 Getting Help

### Communication Channels
- **Issues**: GitHub Issues for bugs/features
- **Discussions**: GitHub Discussions for questions
- **Security**: security@yourdomain.com for vulnerabilities
- **General**: community@yourdomain.com

### Documentation
- [Technical Documentation](README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Security Guide](SECURITY.md)
- [API Documentation](docs/api.md)

## 🏆 Recognition

### Contributors
- Listed in README.md
- Mentioned in release notes
- Invited to project discussions
- Special recognition for significant contributions

### Maintainers
Active contributors may be invited to become maintainers with:
- Commit access
- Review responsibilities
- Project direction input

## 📄 Legal

### License
This project is open source under [LICENSE]. By contributing, you agree:
- Your contributions are your original work
- You grant necessary rights to the project
- Your contributions will be under the same license

### Code of Conduct
We follow the [Contributor Covenant](CODE_OF_CONDUCT.md). Please be:
- Respectful and inclusive
- Professional in communications
- Focused on humanitarian goals
- Supportive of fellow contributors

---

**Thank you for helping us build technology that saves lives and restores mobility! 🦾**

*Every line of code you contribute brings hope to someone in need.*