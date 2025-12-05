# ACCL Frontend Documentation

**Phase 4 - Frontend Implementation**  
**Branch:** `feature/ui-frontend`  
**Date:** December 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Templates](#templates)
4. [Styling](#styling)
5. [JavaScript](#javascript)
6. [Integration Guide](#integration-guide)
7. [Development Guidelines](#development-guidelines)

---

## Overview

The frontend for ACCL is built using:
- **Jinja2 templating engine** (integrated with Flask)
- **Bootstrap 5** for responsive UI components
- **Custom CSS** for branding and layout
- **Vanilla JavaScript** for basic form validation and AJAX operations

The frontend follows the **MVC pattern** with clear separation:
- **Views:** Jinja2 templates render HTML
- **Models:** Flask-SQLAlchemy models (in backend)
- **Controllers:** Flask routes/blueprints handle requests

---

## Project Structure

```
src/app/
├── templates/                    # All HTML templates
│   ├── base.html                # Base template (layout, nav, footer)
│   ├── index.html               # Home page (hero + dashboard)
│   ├── dashboard.html           # User dashboard (role-specific)
│   │
│   ├── auth/
│   │   ├── login.html           # Login form
│   │   └── register.html        # Registration form
│   │
│   ├── assignments.html         # Assignment list with filters
│   ├── assignment_detail.html   # Single assignment view
│   ├── submit_code.html         # Code editor/submission form
│   │
│   ├── submission_results.html  # Test results & feedback
│   ├── plagiarism_report.html   # Similarity detection
│   ├── analytics.html           # Instructor analytics dashboard
│   │
│   ├── profile.html             # User profile & settings
│   ├── 404.html                 # Error page (not found)
│   └── 500.html                 # Error page (server error)
│
└── static/
    ├── css/
    │   └── main.css             # Main stylesheet
    └── js/
        └── main.js              # Main JavaScript
```

---

## Templates

### Base Template (`base.html`)

The master template containing:
- **Navbar** with role-based navigation
- **Flash messages** alert system
- **Main content area**
- **Footer** with project info
- CDN links for Bootstrap 5 and Font Awesome

**Key Features:**
```html
<!-- Navigation bar with dropdowns -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
    <!-- Role-based links -->
    <!-- Dashboard, Assignments, Submissions, Profile -->
</nav>

<!-- Flash message alerts -->
{% with messages = get_flashed_messages(with_categories=true) %}
    <!-- Auto-dismiss alerts -->
{% endwith %}

<!-- Main content block -->
{% block content %}{% endblock %}

<!-- Footer -->
<footer>...</footer>
```

**Usage:**
All other templates extend `base.html`:
```html
{% extends "base.html" %}
{% block title %}Page Title - ACCL{% endblock %}
{% block content %}
    <!-- Page content here -->
{% endblock %}
```

---

### Authentication Templates

#### Login (`auth/login.html`)
- Email and password fields
- "Remember me" checkbox
- Links to register and forgot password
- Demo credentials for testing

#### Register (`auth/register.html`)
- Name, email, password fields
- Account type selector (Student/Instructor)
- Password strength indicator
- Terms and conditions agreement

---

### Assignment Templates

#### Assignment List (`assignments.html`)
- **Filters:** Search, status (active/closed), sort by (due date, recent, name)
- **Card layout** showing:
  - Title and description
  - Due date and status badge
  - Languages supported
  - Student submission status (if student logged in)
  - View/Edit buttons

#### Assignment Detail (`assignment_detail.html`)
- Full assignment description
- Test case preview (visible ones only)
- **Student view:** Submit button, latest submission score
- **Instructor view:** Statistics, submission count, delete button
- Breadcrumb navigation

#### Submit Code (`submit_code.html`)
- **Code editor** (textarea with monospace font)
- Language selector dropdown
- File upload alternative (reads file into editor)
- Character counter (0/100000)
- Previous submission versions in sidebar

---

### Submission & Feedback Templates

#### Submission Results (`submission_results.html`)
- **Overall score** display card
- **Test statistics:** Total, Passed, Failed, Pass Rate
- **Accordion-style test results** showing:
  - Input, Expected Output, Actual Output
  - Stderr (error messages)
  - Runtime in milliseconds
  - Pass/Fail badge
- **AI Hints section** (if available)
- Action buttons (Re-grade, View Code, Re-submit)

#### Plagiarism Report (`plagiarism_report.html`)
- Filter by assignment and similarity threshold
- **Similarity pairs** displayed as cards with color coding:
  - Red (75%+): Very High - Requires Investigation
  - Yellow (50-74%): High - Review Recommended
  - Green (<50%): Low - Likely Independent Work
- Matching code snippets side-by-side
- "Mark as False Positive" button

---

### Instructor Templates

#### Analytics Dashboard (`analytics.html`)
- **Overall statistics:** Class average, total students, submissions, submission rate
- **Performance by Assignment** table:
  - Submissions count
  - Average score
  - Pass rate (with color badges)
  - Median submission time
- **Score Distribution** (placeholder for chart)
- **Performance Tiers:** Count and percentage of students in each tier
- Export CSV button
- Filters by assignment and date range

---

### User Profile (`profile.html`)

**Account Information Section:**
- Name (readonly)
- Role/Account Type
- Email (readonly)
- Password change form

**Notification Preferences:**
- Email on grade
- Email on hint availability
- Email on deadline reminder

**Sidebar:**
- Account statistics (role-specific)
- Quick action buttons (Dashboard, Logout)

---

### Home Page (`index.html`)

**Unauthenticated View:**
- Hero section with CTA buttons (Register/Login)
- Feature cards highlighting key capabilities
- Call-to-action section

**Authenticated View:**
- Welcome greeting with role
- Quick access cards (role-specific):
  - Student: Active Assignments, My Submissions, Average Score, Pending Feedback
  - Instructor: Assignments, Pending Review, Class Average, Plagiarism Flags
- Recent activity timeline
- Quick shortcuts navigation

---

### Error Pages

#### 404.html
- "Page Not Found" message
- Buttons: Go Home, Browse Assignments

#### 500.html
- "Server Error" message
- Error ID for reporting
- Buttons: Go Home, Go Back

---

## Styling

### CSS Organization (`src/app/static/css/main.css`)

**Structure:**
```css
:root { /* CSS Variables */ }
* { /* Reset */ }
body { /* Global styles */ }

/* Navbar Customization */
.navbar { ... }

/* Cards */
.card { ... }
.card-header { ... }

/* Buttons */
.btn { ... }
.btn-primary { ... }

/* Forms */
.form-control { ... }
.form-label { ... }

/* Tables */
.table { ... }

/* Badges */
.badge { ... }

/* Utilities */
.shadow-lg { ... }
.gap-2, .gap-3, .gap-4 { ... }

/* Responsive Design */
@media (max-width: 768px) { ... }

/* Print Styles */
@media print { ... }
```

**Color Scheme:**
- Primary: `#007bff` (Blue)
- Secondary: `#6c757d` (Gray)
- Success: `#28a745` (Green)
- Danger: `#dc3545` (Red)
- Warning: `#ffc107` (Yellow)
- Info: `#17a2b8` (Teal)

**Responsive Classes:**
- `.table-responsive` - Horizontal scroll on mobile
- Bootstrap grid: `col-md-*`, `col-lg-*`
- Utility classes: `d-flex`, `justify-content-center`, `align-items-center`

---

## JavaScript

### Main JavaScript (`src/app/static/js/main.js`)

**Form Validation:**
```javascript
// Bootstrap 5 form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});
```

**Alert Auto-Dismiss:**
```javascript
const alerts = document.querySelectorAll('.alert');
alerts.forEach(alert => {
    if (alert.classList.contains('alert-dismissible')) {
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.display = 'none';
            });
        }
    }
});
```

**AJAX Form Submission Helper:**
```javascript
function submitFormViaAjax(formId, successCallback) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const url = form.getAttribute('action');
        
        fetch(url, {
            method: form.getAttribute('method') || 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && successCallback) {
                successCallback(data);
            }
        });
    });
}
```

**Navigation Highlighting:**
```javascript
function highlightActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        }
    });
}
```

---

## Integration Guide

### Connecting Frontend to Backend

#### 1. Flask Route Setup

```python
# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login
        return redirect(url_for('index'))
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
```

#### 2. Template Context Variables

Pass data from Flask to Jinja2:

```python
@app.route('/assignments')
def assignments():
    assignments = Assignment.query.all()
    return render_template('assignments.html', 
                         assignments=assignments,
                         pagination=pagination)
```

Use in template:
```html
{% for assignment in assignments %}
    <div class="card">
        <h5>{{ assignment.title }}</h5>
        <p>{{ assignment.description }}</p>
    </div>
{% endfor %}
```

#### 3. URL Building with `url_for()`

```html
<!-- In templates, use url_for() instead of hardcoded URLs -->
<a href="{{ url_for('auth.login') }}">Login</a>
<a href="{{ url_for('assignment.view', assignment_id=assignment.id) }}">View Assignment</a>
<form action="{{ url_for('submission.submit', assignment_id=assignment.id) }}" method="POST">
    ...
</form>
```

---

## Development Guidelines

### 1. Template Best Practices

**Use blocks for extensibility:**
```html
{% extends "base.html" %}
{% block title %}Page Title - ACCL{% endblock %}
{% block content %}...{% endblock %}
{% block extra_css %}<!-- page-specific CSS -->{% endblock %}
{% block extra_js %}<!-- page-specific JS -->{% endblock %}
```

**Use macros for reusable components:**
```html
{% macro card(title, content, footer=none) %}
    <div class="card">
        <div class="card-header">{{ title }}</div>
        <div class="card-body">{{ content }}</div>
        {% if footer %}<div class="card-footer">{{ footer }}</div>{% endif %}
    </div>
{% endmacro %}

<!-- Usage -->
{{ card("Assignment 1", "Description here") }}
```

**Include templates for shared sections:**
```html
{% include "partials/pagination.html" %}
{% include "partials/alerts.html" %}
```

### 2. Form Handling

**Use Flask-WTF for forms:**
```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
```

**Render in template:**
```html
<form method="POST" novalidate class="needs-validation">
    {{ form.csrf_token }}
    {{ form.email(class="form-control") }}
    {{ form.password(class="form-control") }}
    <button type="submit" class="btn btn-primary">Login</button>
</form>
```

### 3. Static Files

**Reference static files:**
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
<img src="{{ url_for('static', filename='img/logo.png') }}">
```

### 4. Security

- **CSRF Protection:** Always include `{{ form.csrf_token }}` in forms
- **Escape output:** `{{ variable }}` is auto-escaped in Jinja2
- **Use `|safe` carefully:** Only for trusted HTML content
- **Check permissions:** Use decorators like `@login_required`, `@role_required('instructor')`

### 5. Responsive Design

- Use Bootstrap grid: `col-12`, `col-md-6`, `col-lg-4`
- Mobile-first approach
- Test on mobile (use `{% if is_mobile %}`)
- Bootstrap classes: `d-none d-md-block`, `d-md-none`

### 6. Accessibility

- Use semantic HTML: `<nav>`, `<main>`, `<footer>`
- ARIA labels: `aria-label`, `aria-labelledby`
- Link text descriptive: avoid "Click here"
- Color not only differentiator: use icons + color
- Keyboard navigation support

---

## Common Patterns

### Conditional Role-Based Display

```html
{% if current_user.role == 'student' %}
    <!-- Student-only content -->
{% elif current_user.role == 'instructor' %}
    <!-- Instructor-only content -->
{% elif current_user.role == 'admin' %}
    <!-- Admin-only content -->
{% endif %}
```

### Flash Messages

```html
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ 'danger' if category == 'error' else category }}">
                {{ message }}
            </div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

### Pagination

```html
{% if pagination.pages > 1 %}
    {% for page_num in pagination.iter_pages() %}
        {% if page_num %}
            <a href="{{ url_for('page_route', page=page_num) }}">{{ page_num }}</a>
        {% else %}
            <span>...</span>
        {% endif %}
    {% endfor %}
{% endif %}
```

---

## Testing Frontend

### Manual Testing Checklist

- [ ] Test all links work correctly
- [ ] Form validation displays errors
- [ ] Responsive design on mobile (375px, 768px, 1024px)
- [ ] Navigation updates active state correctly
- [ ] Flash messages display and dismiss
- [ ] Error pages (404, 500) render properly
- [ ] All buttons have hover effects
- [ ] Modals open/close correctly
- [ ] Code editor character counter works
- [ ] File upload reads file into editor

### Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Future Enhancements

- Add chart.js for analytics visualizations
- Implement real-time notifications using WebSockets
- Add code syntax highlighting (highlight.js)
- Implement dark mode toggle
- Add advanced search with filters
- Create mobile app version
- Add drag-and-drop for file uploads
- Implement live code preview

---

**Last Updated:** December 2025  
**Branch:** feature/ui-frontend  
**Status:** In Development
