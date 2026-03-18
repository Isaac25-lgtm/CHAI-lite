# CHAI Uganda -- Field Operations Tool

> A multi-assessment field operations platform built for **CHAI (Clinton Health Access Initiative) Uganda**. Manages participant registration, attendance tracking, and assessment team bank detail collection for field activities across Uganda's 135 districts.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?logo=postgresql&logoColor=white)](https://neon.tech)
[![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?logo=render)](https://render.com)

---

## Key Features

### Multi-Assessment System
- Run multiple assessments concurrently (e.g. *"EDIL Assessment -- Kampala"*, *"Mentorship -- Gulu"*)
- Each assessment has its own name, date range, campaign days (1--30), and unique PIN
- Full data isolation between assessments

### Participant Registration & Attendance
- Register with name, cadre, district, facility, mobile number, and MoMo names
- Track campaign day attendance with checkboxes (up to 30 days)
- Bulk submission from the field -- all participants at a facility submitted together
- All **135 Uganda districts** in a searchable dropdown
- Facility-level Excel download immediately after submission

### Assessment Team Payment (Bank Details)
- Separate bank detail collection for per diem payments
- All **22 Bank of Uganda licensed commercial banks** plus an "Other" option
- Fields: Account Name, Designation, Bank Name, Account Number, Branch

### Manager Dashboard
- Secure admin login via environment variables
- Per-assessment dashboards with full data visibility
- **Filters:** Search (name, phone, facility), district dropdown, date range, reset
- **Actions:** Inline edit any registration, delete individual entries, clear all data
- **Excel Export:** Download filtered data as `.xlsx` with styled headers and checkbox symbols

### Analytics & Charts
All charts display numeric values and percentages directly on the visualization, with a **Save as PNG** button on each.

**Registration Analytics:**
- Enrollment Trend (Line/Area) -- daily registration count over time
- Participants by District (Doughnut) -- distribution with count and percentage
- Participants by Facility (Horizontal Bar) -- facility breakdown with values
- Cadre Breakdown (Pie) -- Nurse, Midwife, CHW distribution
- Attendance per Campaign Day (Stacked Bar) -- Attended vs Absent per day

**Bank Details Analytics:**
- Submission Trend (Line/Area) -- daily submissions over time
- Members by Bank (Doughnut) -- most-used banks with percentages
- Designation Breakdown (Pie) -- TA, District Mentor, etc.
- Members by Branch (Horizontal Bar) -- branch distribution

> Large datasets are handled gracefully: top 10 categories shown, remainder bucketed into "Others". Powered by **Chart.js** with **chartjs-plugin-datalabels**.

---

## How It Works

### Participant Flow
1. Visit the app URL
2. Select an assessment from the dropdown
3. Enter the PIN shared by the manager
4. Choose: **Field Activity** (registration) or **Assessment Team Payment** (bank details)
5. Fill in details and submit
6. Download facility-level Excel after submission

### Manager Flow
1. Visit `/admin` and login
2. Create new assessments (name, dates, campaign days, PIN)
3. Share the PIN with the field team
4. View registration and bank detail dashboards with filters, analytics, and charts
5. Edit or delete any entry
6. Download Excel reports
7. Adjust settings (rename, change dates, update PIN, activate/deactivate, delete)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11, Flask 3.0 |
| Database | PostgreSQL ([Neon](https://neon.tech)) / SQLite (local fallback) |
| ORM | Flask-SQLAlchemy |
| Excel | openpyxl |
| Charts | Chart.js + chartjs-plugin-datalabels |
| Fonts | DM Sans + Instrument Serif (Google Fonts) |
| Hosting | [Render](https://render.com) (Starter plan) |
| WSGI | Gunicorn |

---

## Project Structure

```
CHAI-lite/
|-- app.py                        # Main Flask app (models, routes, Excel builders)
|-- requirements.txt              # Python dependencies
|-- render.yaml                   # Render Blueprint deployment config
|-- runtime.txt                   # Python version specification
|-- templates/
    |-- select_assessment.html    # Landing -- assessment selection + PIN entry
    |-- participant_menu.html     # Post-login menu
    |-- registration.html         # Registration form with attendance checkboxes
    |-- bank_form.html            # Bank detail collection form
    |-- success.html              # Submission success + facility Excel download
    |-- admin_login.html          # Manager login
    |-- admin_assessments.html    # Assessment list + create new
    |-- admin_dashboard.html      # Registration table + filters + analytics
    |-- admin_bank.html           # Bank details table + filters + analytics
    |-- admin_settings.html       # Per-assessment settings
    |-- edit_registration.html    # Edit individual registration
    |-- edit_bank.html            # Edit individual bank detail
```

---

## Database Models

### Assessment

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Auto-increment ID |
| `name` | String(200) | Assessment name |
| `start_date` | Date | Activity start date |
| `end_date` | Date | Activity end date |
| `campaign_days` | Integer | Attendance tracking days (1--30) |
| `pin` | String(10) | Participant access PIN |
| `is_active` | Boolean | Accepting submissions |
| `created_by` | String(100) | Admin who created it |
| `created_at` | DateTime | Creation timestamp |

### Registration

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Auto-increment ID |
| `assessment_id` | Integer (FK) | Links to Assessment |
| `participant_name` | String(200) | Full name |
| `cadre` | String(100) | Role (Nurse, Midwife, CHW, etc.) |
| `district` | String(100) | Uganda district |
| `facility` | String(200) | Health facility |
| `registration_date` | Date | Date of registration |
| `day1` -- `day30` | Boolean | Attendance per campaign day |
| `mobile_number` | String(15) | Phone number (+256...) |
| `mm_registered_names` | String(200) | Mobile Money registered names |
| `submitted_at` | DateTime | Submission timestamp |

### BankDetail

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Auto-increment ID |
| `assessment_id` | Integer (FK) | Links to Assessment |
| `account_name` | String(200) | Name on bank account |
| `designation` | String(100) | Role/title |
| `bank_name` | String(100) | Bank name |
| `account_number` | String(50) | Account number |
| `branch` | String(100) | Bank branch |
| `submitted_at` | DateTime | Submission timestamp |

---

## API Reference

### Participant Routes

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Assessment selection page |
| `POST` | `/join` | Validate PIN and join assessment |
| `GET` | `/menu/<id>` | Participant menu |
| `GET` | `/register/<id>` | Registration form |
| `POST` | `/submit/bulk` | Submit batch of registrations (JSON) |
| `GET` | `/download/facility/<id>/<name>` | Download facility Excel |
| `GET` | `/bank/<id>` | Bank detail form |
| `POST` | `/submit/bank` | Submit bank details (JSON) |

### Admin Routes

| Method | Route | Description |
|--------|-------|-------------|
| `GET/POST` | `/admin/login` | Admin login |
| `GET` | `/admin/logout` | Admin logout |
| `GET` | `/admin/assessments` | List all assessments |
| `POST` | `/admin/assessments/create` | Create new assessment |
| `POST` | `/admin/assessments/<id>/toggle` | Activate/deactivate |
| `POST` | `/admin/assessments/<id>/delete` | Delete assessment + all data |
| `GET` | `/admin/dashboard/<id>` | Registration dashboard |
| `GET/POST` | `/admin/settings/<id>` | Assessment settings |
| `GET` | `/admin/download/excel/<id>` | Download registration Excel |
| `POST` | `/admin/delete/<id>/<reg_id>` | Delete single registration |
| `POST` | `/admin/clear-all/<id>` | Clear all registrations |
| `GET/POST` | `/admin/edit/<id>/<reg_id>` | Edit registration |
| `GET` | `/admin/bank/<id>` | Bank details dashboard |
| `GET` | `/admin/bank/download/<id>` | Download bank payment Excel |
| `POST` | `/admin/bank/delete/<id>/<bd_id>` | Delete single bank detail |
| `POST` | `/admin/bank/clear/<id>` | Clear all bank details |
| `GET/POST` | `/admin/bank/edit/<id>/<bd_id>` | Edit bank detail |

### Utility Routes

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/assessments` | List active assessments (JSON) |
| `GET` | `/healthz` | Health check endpoint |

---

## Getting Started

### Prerequisites
- Python 3.11+
- pip

### Local Development

```bash
# Clone the repository
git clone https://github.com/Isaac25-lgtm/CHAI-lite.git
cd CHAI-lite

# Install dependencies
pip install -r requirements.txt

# Run locally (uses SQLite by default)
python app.py
```

The app runs at `http://127.0.0.1:5000/`

**Default admin credentials (local only):**
`admin` / `admin123`

#### With PostgreSQL

```bash
export DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"
python app.py
```

---

## Deployment on Render

### Using Blueprint (Recommended)

1. Push code to GitHub
2. Go to **Render Dashboard > New > Blueprint**
3. Connect to your GitHub repo
4. Configure:
   - **Blueprint Name:** `chai-field-operations`
   - **Branch:** `main`
5. Set environment variables (see below)
6. Click **Deploy Blueprint**

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes (prod) | `sqlite:///chai_local.db` | PostgreSQL connection string |
| `SECRET_KEY` | Yes (prod) | Auto-generated | Flask session secret |
| `ADMIN_USERNAME` | No | `admin` | Manager login username |
| `ADMIN_PASSWORD` | No | `admin123` | Manager login password |

### Using Neon PostgreSQL

1. Create a free database at [neon.tech](https://neon.tech)
2. Copy the connection string (starts with `postgresql://`)
3. Set it as the `DATABASE_URL` environment variable on Render

> **Auto-migration:** The app automatically adds `day6`--`day30` columns on startup if they don't exist. No manual migration needed.

---

## Security

- Admin credentials loaded from environment variables (never hardcoded in production)
- Database connection string excluded from version control
- Session secret key auto-generated on Render
- PIN-based access control for participant forms
- `@login_required` decorator on all admin routes

---

## Design

- **Color Scheme:** CHAI teal/gold with card-based layout
- **Typography:** DM Sans (body) + Instrument Serif (headings)
- **Responsive:** All pages optimized for phones and tablets
- **Offline-Ready:** Local storage saves form data before submission to prevent data loss
- **Network Indicator:** Online/offline status badge on participant forms

---

## Contributors

| Name | Role | GitHub |
|------|------|--------|
| **Emmanuel Olal** | Senior Associate, Clinton Health Access Initiative | -- |
| **Isaac Omoding** | Data Scientist | [@Isaac25-lgtm](https://github.com/Isaac25-lgtm) |

---

## License

Internal tool for CHAI Uganda field operations.
