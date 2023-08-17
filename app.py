from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterUserForm, LoginUserForm

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 'bad_password'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_RECORD_QUERIES'] = True
app.config['SQLALCHEMY_ECHO'] = True


toolbar = DebugToolbarExtension(app)
connect_db(app)
app.app_context().push()
db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUserForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        
        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        flash('Welcome! Successfully created your account!')
        return redirect('/secret')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.login(username, password)

        if user:
            session['user_id'] = user.id
            flash(f'Welcome back, {user.username}!')
            return redirect('/secret')
        else: 
            form.username.errors = ['You have entered an invalid username or password.']

    return render_template('login.html', form=form)

@app.route('/secret')
def secret():
    try:
        if session['user_id']:
            return render_template('secret.html')
    except:
        flash('You are not authorized to view this page.')
        return redirect('/')

@app.route('/logout')
def logout():
    try:
        session.pop('user_id')
        flash('Goodbye!')
        return redirect('/')
    except:
        return redirect('/')