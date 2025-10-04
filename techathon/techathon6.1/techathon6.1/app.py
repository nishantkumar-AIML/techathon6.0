from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from utils.mock_social import aggregate_external_info, mock_search_by_name_or_dept
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///providers.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'doctor'
    # Doctor profile fields (nullable)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    whatsapp = db.Column(db.String(50))
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    hospital = db.Column(db.String(200))
    experience = db.Column(db.String(50))
    license_no = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    email_public = db.Column(db.String(150))
    instagram = db.Column(db.String(200))
    telegram = db.Column(db.String(200))
    youtube = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    profile_image = db.Column(db.String(300))  # path to image

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize DB if needed
@app.before_first_request
def create_tables():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role','user')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name') or None
        if User.query.filter_by(email=email).first():
            flash('Email already registered','danger')
            return redirect(url_for('register'))
        user = User(email=email, role=role, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully. Please login.','success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid credentials','danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Logged in','success')
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out','info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    # Only doctors can edit full profile; ordinary users can edit limited info
    if request.method=='POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.whatsapp = request.form.get('whatsapp')
        current_user.address = request.form.get('address')
        current_user.city = request.form.get('city')
        current_user.hospital = request.form.get('hospital')
        current_user.experience = request.form.get('experience')
        current_user.license_no = request.form.get('license_no')
        current_user.specialization = request.form.get('specialization')
        current_user.email_public = request.form.get('email_public')
        current_user.instagram = request.form.get('instagram')
        current_user.telegram = request.form.get('telegram')
        current_user.youtube = request.form.get('youtube')
        current_user.facebook = request.form.get('facebook')
        current_user.twitter = request.form.get('twitter')
        # profile image upload simple (saved to static/uploads)
        file = request.files.get('profile_image')
        if file and file.filename:
            upload_dir = os.path.join('static','uploads')
            os.makedirs(upload_dir, exist_ok=True)
            path = os.path.join(upload_dir, file.filename)
            file.save(path)
            current_user.profile_image = path
        db.session.commit()
        flash('Profile updated','success')
        return redirect(url_for('profile', user_id=current_user.id))
    return render_template('edit_profile.html')

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    # Aggregate external info (mock) and compute confidence
    external = aggregate_external_info(user)
    # Compute a naive confidence %
    confidence = external.get('confidence',0)
    return render_template('profile.html', prof=user, external=external, confidence=confidence)

@app.route('/search', methods=['GET','POST'])
@login_required
def search():
    q = request.args.get('q') or request.form.get('q')
    dept = request.form.get('dept') if request.method=='POST' else None
    results = []
    if q or dept:
        results = mock_search_by_name_or_dept(q, dept)
    return render_template('search.html', results=results)

# Static file route for downloads (simple)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
