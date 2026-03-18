# CHAI Uganda - Field Operations Tool

A multi-assessment field operations platform built for **CHAI (Clinton Health Access Initiative) Uganda**. Manages participant registration, attendance tracking, and assessment team bank detail collection for field activities across Uganda.

---

## Features

### Multi-Assessment System
- Multiple assessments can run concurrently (e.g. "EDIL Assessment - Kampala", "Mentorship - Gulu")
- Each assessment has its own name, date range, campaign days (1-30), and unique PIN
- Managers create assessments and share PINs with field teams
- Participants select their assessment from a dropdown and enter the PIN to access it
- Full data isolation between assessments

### Participant Registration & Attendance
- Participants register with: Name, Cadre, District, Facility, Mobile Number, MoMo Names
- Campaign day attendance tracked with checkboxes (1st, 2nd, 3rd... up to 30th day)
- Bulk submission from field - all participants at a facility submitted together
- All 135 Uganda districts available in a searchable dropdown
- Facility-level Excel download for field teams after submission

### Assessment Team Payment (Bank Details)
- Separate bank detail collection form for per diem payments
- All 22 Bank of Uganda licensed commercial banks:
  - Absa Bank Uganda Limited
  - Bank of Africa Uganda Limited
  - Bank of Baroda Uganda Limited
  - Bank of India (Uganda) Limited
  - Cairo Bank Uganda
  - Centenary Bank
  - Citibank Uganda Limited
  - DFCU Bank
  - Diamond Trust Bank (DTB) Uganda
  - Ecobank Uganda Limited
  - Equity Bank Uganda Limited
  - Exim Bank Uganda Limited
  - Housing Finance Bank
  - I&M Bank Uganda
  - KCB Bank Uganda Limited
  - NCBA Bank Uganda Limited
  - Pearl Bank Uganda Limited
  - Salaam Bank Uganda
  - Stanbic Bank Uganda Limited
  - Standard Chartered Bank Uganda
  - Tropical Bank Limited
  - United Bank for Africa (UBA) Uganda
- "Other" option with custom text input for unlisted banks
- Fields: Account Name, Designation, Bank Name, Account Number, Branch

### Manager Dashboard
- Secure admin login (credentials via environment variables)
- Per-assessment dashboards with full data visibility
- **Stats Cards**: Total Participants, Registered Today, Districts Covered, Facilities Reached, Bank Details Submitted, Filtered Results
- **Filters**: Search (name, phone, facility), District dropdown, Date range (From/To), Reset button
- **Edit**: Inline edit any registration - change name, cadre, district, facility, phone, MoMo names, and tick/untick attendance day checkboxes
- **Delete**: Delete individual registrations or clear all data
- **Excel Download**: Download filtered data as .xlsx with proper formatting, checkbox symbols, and styled headers

### Manager Analytics (Registration Dashboard)
All charts display numeric values/percentages directly on the visualization:
1. **Enrollment Trend** (Line/Area chart) - Daily registration count over time with data points
2. **Participants by District** (Doughnut chart) - District distribution with count and percentage
3. **Participants by Facility** (Horizontal Bar chart) - Facility breakdown with values
4. **Cadre Breakdown** (Pie chart) - Nurse, Midwife, CHW distribution with percentages
5. **Attendance per Campaign Day** (Stacked Bar chart) - Attended vs Absent per day with counts

### Manager Analytics (Bank Details)
1. **Submission Trend** (Line/Area chart) - Daily bank detail submissions over time
2. **Members by Bank** (Doughnut chart) - Which banks are most used with percentages
3. **Designation Breakdown** (Pie chart) - TA, District Mentor, etc. with percentages
4. **Members by Branch** (Horizontal Bar chart) - Branch distribution with values

### Chart Features
- All charts show data labels (counts and percentages) directly on the visualization
- Each chart has a **Save** button to download as PNG image
- Charts are named descriptively (e.g. CHAI_District_Distribution_AssessmentName.png)
- Large datasets handled gracefully: top 10 categories shown, rest bucketed into "Others"
- Charts powered by Chart.js with chartjs-plugin-datalabels

### Bank Details Manager View
- Same filter system as registrations: Search, Bank dropdown, Date range
- Stats: Total Team Members, Filtered Results, Banks Used, Branches
- Edit any bank detail entry (account name, designation, bank, account number, branch)
- Download filtered payment Excel

### Excel Downloads
- Registration Excel: Formatted with blue headers, checkbox symbols, column widths, borders
- Bank Payment Excel: Professional payment tracker format with perdiem columns
- Both support filtered downloads (only exports what's currently filtered)

### Participant Flow
1. Visit the app URL
2. Select assessment from dropdown
3. Enter the PIN shared by the manager
4. Choose: **Field Activity** (registration) or **Assessment Team Payment** (bank details)
5. Fill in details and submit
6. Download facility-level Excel after submission

### Manager Flow
1. Visit `/admin` and login
2. Create new assessments (name, dates, campaign days, PIN)
3. Share PIN with field team
4. View registrations dashboard with filters, analytics, and charts
5. View bank details with filters and analytics
6. Edit or delete any entry
7. Download Excel reports
8. Adjust settings (rename assessment, change dates, update PIN, change campaign days)
9. Activate/deactivate or delete assessments

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| Database | PostgreSQL (Neon) / SQLite (local fallback) |
| ORM | Flask-SQLAlchemy |
| Excel | openpyxl |
| Charts | Chart.js + chartjs-plugin-datalabels |
| Fonts | DM Sans + Instrument Serif (Google Fonts) |
| Hosting | Render (Starter plan) |
| WSGI | Gunicorn |

---

## Project Structure

```
your-project/
  app.py                          # Main Flask application (models, routes, Excel builders)
  requirements.txt                # Python dependencies
  render.yaml                     # Render Blueprint deployment config
  runtime.txt                     # Python version specification
  templates/
    select_assessment.html        # Landing page - assessment selection + PIN entry
    participant_menu.html         # Post-login menu: Field Activity or Bank Details
    registration.html             # Participant registration form with attendance checkboxes
    bank_form.html                # Bank detail collection form
    success.html                  # Submission success page with facility Excel download
    admin_login.html              # Manager login page
    admin_assessments.html        # Assessment list + create new assessment
    admin_dashboard.html          # Registration data table + filters + analytics charts
    admin_bank.html               # Bank details table + filters + analytics charts
    admin_settings.html           # Per-assessment settings (name, dates, days, PIN)
    edit_registration.html        # Edit individual registration (all fields + day checkboxes)
    edit_bank.html                # Edit individual bank detail entry
```

---

## Database Models

### Assessment
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment ID |
| name | String(200) | Assessment name |
| start_date | Date | Activity start date |
| end_date | Date | Activity end date |
| campaign_days | Integer | Number of attendance tracking days (1-30) |
| pin | String(10) | Participant access PIN |
| is_active | Boolean | Whether assessment is accepting submissions |
| created_by | String(100) | Admin username who created it |
| created_at | DateTime | Creation timestamp |

### Registration
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment ID |
| assessment_id | Integer (FK) | Links to Assessment |
| participant_name | String(200) | Full name |
| cadre | String(100) | Role (Nurse, Midwife, CHW, etc.) |
| district | String(100) | Uganda district |
| facility | String(200) | Health facility name |
| registration_date | Date | Date of registration |
| day1 - day30 | Boolean | Attendance for each campaign day |
| mobile_number | String(15) | Phone number (+256...) |
| mm_registered_names | String(200) | Mobile Money registered names |
| submitted_at | DateTime | Submission timestamp |

### BankDetail
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment ID |
| assessment_id | Integer (FK) | Links to Assessment |
| account_name | String(200) | Name on bank account |
| designation | String(100) | Role/title |
| bank_name | String(100) | Bank name |
| account_number | String(50) | Account number |
| branch | String(100) | Bank branch |
| submitted_at | DateTime | Submission timestamp |

---

## API Routes

### Participant Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Assessment selection page |
| POST | `/join` | Validate PIN and join assessment |
| GET | `/menu/<id>` | Participant menu (Field Activity / Bank Details) |
| GET | `/register/<id>` | Registration form |
| POST | `/submit/bulk` | Submit batch of registrations (JSON) |
| GET | `/download/facility/<id>/<name>` | Download facility Excel |
| GET | `/bank/<id>` | Bank detail form |
| POST | `/submit/bank` | Submit bank details (JSON) |

### Admin Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/admin/login` | Admin login |
| GET | `/admin/logout` | Admin logout |
| GET | `/admin/assessments` | List all assessments |
| POST | `/admin/assessments/create` | Create new assessment |
| POST | `/admin/assessments/<id>/toggle` | Activate/deactivate assessment |
| POST | `/admin/assessments/<id>/delete` | Delete assessment + all data |
| GET | `/admin/dashboard/<id>` | Registration dashboard with filters + charts |
| GET/POST | `/admin/settings/<id>` | Assessment settings |
| GET | `/admin/download/excel/<id>` | Download registration Excel |
| POST | `/admin/delete/<id>/<reg_id>` | Delete single registration |
| POST | `/admin/clear-all/<id>` | Clear all registrations |
| GET/POST | `/admin/edit/<id>/<reg_id>` | Edit registration |
| GET | `/admin/bank/<id>` | Bank details dashboard with filters + charts |
| GET | `/admin/bank/download/<id>` | Download bank payment Excel |
| POST | `/admin/bank/delete/<id>/<bd_id>` | Delete single bank detail |
| POST | `/admin/bank/clear/<id>` | Clear all bank details |
| GET/POST | `/admin/bank/edit/<id>/<bd_id>` | Edit bank detail |

### API Routes
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/assessments` | List active assessments (JSON) |
| GET | `/healthz` | Health check endpoint |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes (production) | `sqlite:///chai_local.db` | PostgreSQL connection string |
| `SECRET_KEY` | Yes (production) | Auto-generated | Flask session secret |
| `ADMIN_USERNAME` | No | `admin` | Manager login username |
| `ADMIN_PASSWORD` | No | `admin123` | Manager login password |
| `PYTHON_VERSION` | No | `3.11.9` | Python version for Render |

---

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/Isaac25-lgtm/CHAI-lite.git
cd CHAI-lite

# Install dependencies
pip install -r requirements.txt

# Run locally (uses SQLite by default)
python app.py

# Or with PostgreSQL
export DATABASE_URL="postgresql://user:pass@host/dbname?sslmode=require"
python app.py
```

The app runs at `http://127.0.0.1:5000/`

### Default Admin Credentials (Local)
- **Username**: `admin`
- **Password**: `admin123`

---

## Deployment on Render

### Using Blueprint (Recommended)
1. Push code to GitHub
2. Go to Render Dashboard > **New** > **Blueprint**
3. Connect to your GitHub repo
4. Fill in:
   - **Blueprint Name**: `chai-field-operations`
   - **Branch**: `main`
   - **DATABASE_URL**: Your Neon PostgreSQL connection string
   - **ADMIN_USERNAME**: Your chosen admin username
   - **ADMIN_PASSWORD**: Your chosen secure password
5. Click **Deploy Blueprint**

### Environment Variables on Render
Set these in the Render dashboard under your service > **Environment**:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://user:pass@host/dbname?sslmode=require` |
| `ADMIN_USERNAME` | Your admin username |
| `ADMIN_PASSWORD` | Your secure admin password |
| `SECRET_KEY` | Auto-generated by Render |

### Using Neon PostgreSQL
1. Create a free database at [neon.tech](https://neon.tech)
2. Copy the connection string (starts with `postgresql://`)
3. Paste it as the `DATABASE_URL` environment variable on Render

---

## Database Migration
The app automatically adds day6-day30 columns to the registration table on startup if they don't exist (PostgreSQL only). No manual migration needed.

---

## Security Notes
- Admin credentials are loaded from environment variables (not hardcoded in production)
- Database connection string is never committed to the repository
- Session secret key is auto-generated on Render
- PIN-based access control for participant forms
- Login required decorator on all admin routes

---

## UI/UX Design
- **Design System**: CHAI teal/gold color scheme with card-based layout
- **Fonts**: DM Sans (body) + Instrument Serif (headings) from Google Fonts
- **Mobile Responsive**: All pages work on phones and tablets
- **Checkbox Format**: Uses Unicode checkbox symbols in both UI and Excel downloads - same format on phone and manager side
- **Online/Offline Indicator**: Shows network status badge on participant forms
- **Local Storage**: Participant forms save data locally before submission to prevent data loss

---

## License
Internal tool for CHAI Uganda field operations.
