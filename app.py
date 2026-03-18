from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import io
import os
from functools import wraps
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Use DATABASE_URL env var in production (Neon/Render), SQLite locally as fallback
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///chai_local.db')

# Fix for older postgres:// URIs (Render/Heroku style)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True, 'pool_recycle': 300}

db = SQLAlchemy(app)

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


def ordinal(n):
    ords = ['', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th']
    return ords[n] if n < len(ords) else f'{n}th'


# ── Models ──────────────────────────────────────────────────────────

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    campaign_days = db.Column(db.Integer, default=3)
    pin = db.Column(db.String(10), nullable=False)
    created_by = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    registrations = db.relationship('Registration', backref='assessment', lazy=True)

    @property
    def dates_label(self):
        """Format dates nicely for display"""
        if self.start_date and self.end_date:
            return f"{self.start_date.strftime('%d %b %Y')} to {self.end_date.strftime('%d %b %Y')}"
        elif self.start_date:
            return f"From {self.start_date.strftime('%d %b %Y')}"
        return ''

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dates_label': self.dates_label,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else '',
            'campaign_days': self.campaign_days,
            'pin': self.pin,
            'is_active': self.is_active,
        }


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    participant_name = db.Column(db.String(200), nullable=False)
    cadre = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    facility = db.Column(db.String(200), nullable=False)
    registration_date = db.Column(db.Date, nullable=False)
    day1 = db.Column(db.Boolean, default=False)
    day2 = db.Column(db.Boolean, default=False)
    day3 = db.Column(db.Boolean, default=False)
    day4 = db.Column(db.Boolean, default=False)
    day5 = db.Column(db.Boolean, default=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    mm_registered_names = db.Column(db.String(200), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'assessment_id': self.assessment_id,
            'participant_name': self.participant_name,
            'cadre': self.cadre,
            'district': self.district,
            'facility': self.facility,
            'registration_date': self.registration_date.strftime('%Y-%m-%d'),
            'day1': self.day1, 'day2': self.day2, 'day3': self.day3,
            'day4': self.day4, 'day5': self.day5,
            'mobile_number': self.mobile_number,
            'mm_registered_names': self.mm_registered_names,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        }


with app.app_context():
    db.create_all()


# ── Auth ────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ── Excel builder ───────────────────────────────────────────────────

def build_excel(registrations, campaign_days, sheet_title="Registration & Attendance"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title

    header_fill = PatternFill(start_color="2B5097", end_color="2B5097", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell_font = Font(name="Calibri", size=10)
    cell_alignment = Alignment(vertical="center", wrap_text=True)
    center_alignment = Alignment(horizontal="center", vertical="center")
    med_border = Border(
        left=Side(style='medium', color='000000'), right=Side(style='medium', color='000000'),
        top=Side(style='medium', color='000000'), bottom=Side(style='medium', color='000000'))
    thin_border = Border(
        left=Side(style='thin', color='000000'), right=Side(style='thin', color='000000'),
        top=Side(style='thin', color='000000'), bottom=Side(style='thin', color='000000'))
    checked_font = Font(name="Calibri", size=14, bold=True, color="008000")
    unchecked_font = Font(name="Calibri", size=14, color="AAAAAA")

    headers = ['No.', "Participant\u2019s Name", 'Cadre', 'Duty Station', 'District',
               'Mobile Number Registered', 'Names Registered (First & Last Names)']
    for day in range(1, campaign_days + 1):
        headers.append(ordinal(day))
    ws.append(headers)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = med_border
    ws.row_dimensions[1].height = 38

    for idx, reg in enumerate(registrations, start=1):
        row = [idx, reg.participant_name, reg.cadre, reg.facility, reg.district,
               reg.mobile_number, reg.mm_registered_names]
        for day in range(1, campaign_days + 1):
            row.append('\u2611' if getattr(reg, f'day{day}', False) else '\u2610')
        ws.append(row)

        row_num = idx + 1
        for col_num, cell in enumerate(ws[row_num], start=1):
            cell.font = cell_font
            cell.border = thin_border
            cell.alignment = cell_alignment
            if col_num == 1:
                cell.alignment = center_alignment
            if 7 < col_num <= 7 + campaign_days:
                cell.alignment = center_alignment
                cell.font = checked_font if cell.value == '\u2611' else unchecked_font
        ws.row_dimensions[row_num].height = 22

    base_widths = [5, 25, 16, 21, 16, 21, 30]
    for i, w in enumerate(base_widths + [8] * campaign_days, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    return wb


# ── Participant routes ──────────────────────────────────────────────

@app.route('/')
def index():
    """Show assessment selector for participants"""
    assessments = Assessment.query.filter_by(is_active=True).order_by(Assessment.created_at.desc()).all()
    return render_template('select_assessment.html', assessments=assessments)


@app.route('/join', methods=['POST'])
def join_assessment():
    """Participant enters assessment PIN to access form"""
    assessment_id = request.form.get('assessment_id')
    pin = request.form.get('pin', '').strip()

    if not assessment_id:
        flash('Please select an assessment.', 'error')
        return redirect(url_for('index'))

    assessment = Assessment.query.get(assessment_id)
    if not assessment or not assessment.is_active:
        flash('Assessment not found or inactive.', 'error')
        return redirect(url_for('index'))

    if assessment.pin != pin:
        flash('Incorrect PIN. Please get the correct PIN from your manager.', 'error')
        return redirect(url_for('index'))

    # Store in session
    session['participant_assessment_id'] = assessment.id
    return redirect(url_for('registration_form', assessment_id=assessment.id))


@app.route('/register/<int:assessment_id>')
def registration_form(assessment_id):
    """Show registration form for a specific assessment"""
    # Verify session
    if session.get('participant_assessment_id') != assessment_id:
        flash('Please select and enter PIN for your assessment.', 'error')
        return redirect(url_for('index'))

    assessment = Assessment.query.get_or_404(assessment_id)
    if not assessment.is_active:
        flash('This assessment is no longer active.', 'error')
        return redirect(url_for('index'))

    return render_template('registration.html',
                         assessment=assessment,
                         campaign_days=assessment.campaign_days,
                         activity_name=assessment.name,
                         activity_dates=assessment.dates_label)


@app.route('/submit/bulk', methods=['POST'])
def submit_bulk_registration():
    try:
        data = request.get_json()
        participants = data.get('participants', [])
        assessment_id = data.get('assessment_id')

        if not participants:
            return jsonify({'success': False, 'error': 'No participants provided'}), 400
        if not assessment_id:
            return jsonify({'success': False, 'error': 'No assessment specified'}), 400

        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({'success': False, 'error': 'Assessment not found'}), 404

        facility = participants[0].get('facility', 'Unknown')
        registrations = []

        for p in participants:
            reg_date = datetime.strptime(p.get('registration_date'), '%Y-%m-%d').date()
            registration = Registration(
                assessment_id=assessment_id,
                participant_name=p.get('participant_name'),
                cadre=p.get('cadre'),
                district=p.get('district'),
                facility=p.get('facility'),
                registration_date=reg_date,
                day1=p.get('day1', False), day2=p.get('day2', False),
                day3=p.get('day3', False), day4=p.get('day4', False),
                day5=p.get('day5', False),
                mobile_number=p.get('mobile_number'),
                mm_registered_names=p.get('mm_registered_names')
            )
            db.session.add(registration)
            registrations.append(registration)

        db.session.commit()
        return jsonify({
            'success': True, 'facility': facility,
            'count': len(registrations),
            'data': [r.to_dict() for r in registrations]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/download/facility/<int:assessment_id>/<facility_name>')
def download_facility_data(assessment_id, facility_name):
    try:
        assessment = Assessment.query.get_or_404(assessment_id)
        registrations = Registration.query.filter_by(
            assessment_id=assessment_id, facility=facility_name
        ).order_by(Registration.submitted_at.desc()).all()

        if not registrations:
            return jsonify({'success': False, 'error': 'No data found'}), 404

        wb = build_excel(registrations, assessment.campaign_days, "Facility Data")
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        safe_name = facility_name.replace(' ', '_').replace('/', '_')
        filename = f'CHAI_{safe_name}_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        return send_file(output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── Admin routes ────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_assessments'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/assessments')
@login_required
def admin_assessments():
    """List all assessments for this manager"""
    assessments = Assessment.query.order_by(Assessment.created_at.desc()).all()
    # Get registration counts per assessment
    counts = {}
    for a in assessments:
        counts[a.id] = Registration.query.filter_by(assessment_id=a.id).count()
    return render_template('admin_assessments.html', assessments=assessments, counts=counts)


@app.route('/admin/assessments/create', methods=['POST'])
@login_required
def create_assessment():
    name = request.form.get('name', '').strip()
    start_date_str = request.form.get('start_date', '').strip()
    end_date_str = request.form.get('end_date', '').strip()
    campaign_days = request.form.get('campaign_days', '3')
    pin = request.form.get('pin', '').strip()

    if not name:
        flash('Assessment name is required.', 'error')
        return redirect(url_for('admin_assessments'))

    # Parse dates
    start_date = None
    end_date = None
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if start_date and end_date and end_date < start_date:
            flash('End date cannot be before start date.', 'error')
            return redirect(url_for('admin_assessments'))
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('admin_assessments'))

    try:
        campaign_days_int = int(campaign_days)
        if campaign_days_int < 1 or campaign_days_int > 5:
            raise ValueError
    except ValueError:
        flash('Campaign days must be between 1 and 5.', 'error')
        return redirect(url_for('admin_assessments'))

    if not pin or len(pin) < 3:
        flash('PIN must be at least 3 characters.', 'error')
        return redirect(url_for('admin_assessments'))

    existing = Assessment.query.filter_by(pin=pin, is_active=True).first()
    if existing:
        flash('This PIN is already in use by another active assessment. Choose a different one.', 'error')
        return redirect(url_for('admin_assessments'))

    assessment = Assessment(
        name=name,
        start_date=start_date,
        end_date=end_date,
        campaign_days=campaign_days_int,
        pin=pin,
        created_by=session.get('admin_user', 'admin')
    )
    db.session.add(assessment)
    db.session.commit()
    flash(f'Assessment "{name}" created! PIN: {pin}', 'success')
    return redirect(url_for('admin_assessments'))


@app.route('/admin/assessments/<int:assessment_id>/toggle', methods=['POST'])
@login_required
def toggle_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    assessment.is_active = not assessment.is_active
    db.session.commit()
    status = 'activated' if assessment.is_active else 'deactivated'
    flash(f'Assessment "{assessment.name}" {status}.', 'success')
    return redirect(url_for('admin_assessments'))


@app.route('/admin/assessments/<int:assessment_id>/delete', methods=['POST'])
@login_required
def delete_assessment(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    # Delete all registrations first
    Registration.query.filter_by(assessment_id=assessment_id).delete()
    db.session.delete(assessment)
    db.session.commit()
    flash(f'Assessment "{assessment.name}" and all its data deleted.', 'success')
    return redirect(url_for('admin_assessments'))


@app.route('/admin/dashboard/<int:assessment_id>')
@login_required
def admin_dashboard(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    campaign_days = assessment.campaign_days

    search = request.args.get('search', '')
    district = request.args.get('district', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Registration.query.filter_by(assessment_id=assessment_id)
    if search:
        query = query.filter(db.or_(
            Registration.participant_name.ilike(f'%{search}%'),
            Registration.mobile_number.ilike(f'%{search}%'),
            Registration.facility.ilike(f'%{search}%')
        ))
    if district:
        query = query.filter(Registration.district == district)
    if date_from:
        try:
            query = query.filter(Registration.registration_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Registration.registration_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    registrations = query.order_by(Registration.submitted_at.desc()).all()

    districts = [d[0] for d in db.session.query(Registration.district).filter_by(
        assessment_id=assessment_id).distinct().order_by(Registration.district).all()]
    total_count = Registration.query.filter_by(assessment_id=assessment_id).count()
    today = datetime.utcnow().date()
    today_count = Registration.query.filter_by(assessment_id=assessment_id).filter(
        db.func.date(Registration.submitted_at) == today).count()

    thirty_days_ago = today - timedelta(days=30)
    daily_registrations = db.session.query(
        db.func.date(Registration.submitted_at).label('date'),
        db.func.count(Registration.id).label('count')
    ).filter(Registration.assessment_id == assessment_id,
             Registration.submitted_at >= thirty_days_ago
    ).group_by(db.func.date(Registration.submitted_at)).order_by('date').all()

    district_stats = db.session.query(
        Registration.district, db.func.count(Registration.id).label('count')
    ).filter_by(assessment_id=assessment_id
    ).group_by(Registration.district).order_by(db.func.count(Registration.id).desc()).limit(10).all()

    facility_stats = db.session.query(
        Registration.facility, db.func.count(Registration.id).label('count')
    ).filter_by(assessment_id=assessment_id
    ).group_by(Registration.facility).order_by(db.func.count(Registration.id).desc()).limit(10).all()

    return render_template('admin_dashboard.html',
        assessment=assessment,
        registrations=registrations,
        total_count=total_count,
        today_count=today_count,
        filtered_count=len(registrations),
        search=search, districts=districts,
        selected_district=district,
        date_from=date_from, date_to=date_to,
        daily_registrations=daily_registrations,
        district_stats=district_stats,
        facility_stats=facility_stats,
        campaign_days=campaign_days)


@app.route('/admin/settings/<int:assessment_id>', methods=['GET', 'POST'])
@login_required
def admin_settings(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)

    if request.method == 'POST':
        name = request.form.get('activity_name', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        campaign_days = request.form.get('campaign_days', '3')
        pin = request.form.get('pin', '').strip()

        if name:
            assessment.name = name
        try:
            if start_date_str:
                assessment.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if end_date_str:
                assessment.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
        if pin and len(pin) >= 3:
            # Check uniqueness
            existing = Assessment.query.filter(
                Assessment.pin == pin, Assessment.is_active == True,
                Assessment.id != assessment_id).first()
            if existing:
                flash('PIN already in use by another assessment.', 'error')
                return redirect(url_for('admin_settings', assessment_id=assessment_id))
            assessment.pin = pin

        try:
            cd = int(campaign_days)
            if 1 <= cd <= 5:
                assessment.campaign_days = cd
        except ValueError:
            pass

        db.session.commit()
        flash('Settings updated!', 'success')
        return redirect(url_for('admin_settings', assessment_id=assessment_id))

    return render_template('admin_settings.html', assessment=assessment,
                         campaign_days=assessment.campaign_days,
                         activity_name=assessment.name)


@app.route('/admin/download/excel/<int:assessment_id>')
@login_required
def download_excel(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)

    district = request.args.get('district', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Registration.query.filter_by(assessment_id=assessment_id)
    if district:
        query = query.filter(Registration.district == district)
    if date_from:
        try:
            query = query.filter(Registration.registration_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Registration.registration_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    registrations = query.order_by(Registration.submitted_at.desc()).all()
    wb = build_excel(registrations, assessment.campaign_days)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    safe_name = assessment.name.replace(' ', '_')
    filename = f'CHAI_{safe_name}_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
    return send_file(output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, download_name=filename)


@app.route('/admin/delete/<int:assessment_id>/<int:reg_id>', methods=['POST'])
@login_required
def delete_registration(assessment_id, reg_id):
    registration = Registration.query.get_or_404(reg_id)
    db.session.delete(registration)
    db.session.commit()
    flash('Registration deleted.', 'success')
    return redirect(url_for('admin_dashboard', assessment_id=assessment_id))


@app.route('/admin/clear-all/<int:assessment_id>', methods=['POST'])
@login_required
def clear_all(assessment_id):
    Registration.query.filter_by(assessment_id=assessment_id).delete()
    db.session.commit()
    flash('All registrations cleared.', 'success')
    return redirect(url_for('admin_dashboard', assessment_id=assessment_id))


# ── API ─────────────────────────────────────────────────────────────

@app.route('/api/assessments')
def api_assessments():
    assessments = Assessment.query.filter_by(is_active=True).all()
    return jsonify([a.to_dict() for a in assessments])


@app.route('/healthz')
def healthz():
    return jsonify(status='ok')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
