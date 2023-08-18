from flask import Flask, render_template, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterUserForm, LoginUserForm, FeedbackForm
from datetime import datetime

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
        
        if User.check_for_existing_username(username):
            form.username.errors = ['Username already exists. Please use another username.']
            return render_template('register.html', form=form)
        elif User.check_for_existing_email(email):
            form.email.errors = ['Email already exists. Please use another email.']
            return render_template('register.html', form=form)
        else:
            user = User.register(username, password, email, first_name, last_name)
            db.session.add(user)
            db.session.commit()

            session['username'] = user.username
            flash(f'Welcome, {username}! Successfully created your account!')
            return redirect(f'/users/{username}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.login(username, password)

        if user:
            session['username'] = user.username
            flash(f'Welcome back, {username}!')
            return redirect(f'/users/{username}')
        else: 
            form.username.errors = ['You have entered an invalid username or password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    try:
        if session['username']:
            session.pop('username')
            flash(f'Goodbye!')
            return redirect('/')
    except:
        return redirect('/')

@app.route('/users/<username>')
def user_details(username):
    user = User.query.filter_by(username=username).first()
    try:
        if session['username'] == user.username:
            return render_template('user_details.html', user=user)
        else:
            flash('You are not authorized to view this page.')
            return redirect('/')
    except:
        flash('You are not authorized to view this page.')
        return redirect('/')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()

    flash(f'{username} was successfully deleted.')
    return redirect('/logout')

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        
        feedback = Feedback.query.get(feedback_id)
        feedback.title = title
        feedback.content = content
        db.session.commit()

        flash('Feedback updated!')
        return redirect(f'/users/{feedback.user.username}')

    return render_template(f'/feedback/{feedback_id}/update', form=form)