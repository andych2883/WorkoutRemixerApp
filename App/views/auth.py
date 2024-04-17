from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, get_jwt_identity
from werkzeug.urls import url_parse
from sqlalchemy import or_
from App.models import db
from App.database import db

from App.controllers import (
    login, signup
)

from App.models import (
    Workout,
    Routine,
    RoutineWorkout,
    User
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


'''
Page/Action Routes
'''
@auth_views.route('/index', methods=['GET'])
def index_page():
    return render_template('index.html')

@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template('message.html', title="Identify", message=f"You are logged in as {current_user.id} - {current_user.username}")

@auth_views.route('/signup', methods=['POST'])
def signup_action():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        flash('Username and password are required')
        return redirect(url_for('auth_views.signup_page'))
    if signup(username, password):
        flash('Signup successful! Please login.')
        return redirect(url_for('auth_views.index_page'))
    else:
        flash('Username already exists. Please choose a different username.')
        return redirect(url_for('auth_views.signup_page'))    

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    response = redirect(url_for('auth_views.home_page'))
    #response = redirect(request.referrer)
    if not token:
        flash('Bad username or password given'), 401
    else:
        flash('Login Successful')
        set_access_cookies(response, token) 
    return response

@auth_views.route('/signup', methods=['POST'])
def signup_action():
    username = request.form.get('new_username')  
    password = request.form.get('new_password') 

    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('Username already exists. Please choose a different one.', 'error')
        return redirect(url_for('auth_views.home_page'))

    # Create new user
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    # Log in the new user
    token = login(username, password)
    if not token:
        flash('Failed to log in after signup.', 'error')
        return redirect(url_for('auth_views.home_page'))

    # Redirect to home page
    response = redirect(url_for('auth_views.home_page'))
    flash('Signup successful. Welcome!', 'success')
    set_access_cookies(response, token)
    return response

@auth_views.route('/home', methods=['GET', 'POST'])
@jwt_required()
def home_page():
    search_query = request.args.get('search', default='', type=str)
    workouts = None
    selected_workout = None
    user_routines = Routine.query.filter_by(user_id=current_user.id).all()
    selected_routine = None

    if request.method == 'POST':
        if 'delete_routine' in request.form:
            routine_id = request.form.get('routine_id')
            RoutineWorkout.query.filter_by(routine_id=routine_id).delete()
            db.session.commit()
            Routine.query.filter_by(id=routine_id).delete()
            db.session.commit()
            flash('Routine deleted successfully.', 'success')
            return redirect(url_for('auth_views.home_page'))

        if 'delete_workout_from_routine' in request.form:
            routine_workout_id = request.form.get('routine_workout_id')
            RoutineWorkout.query.filter_by(id=routine_workout_id).delete()
            db.session.commit()
            flash('Workout removed from routine successfully.', 'success')
            return redirect(request.referrer or url_for('auth_views.home_page'))

        if 'routine_workout_id' in request.form and request.form.get('action') == 'update':
            routine_workout_id = request.form.get('routine_workout_id', type=int)
            reps = request.form.get('reps', type=int)
            sets = request.form.get('sets', type=int)
            # Validate input
            if reps is not None and sets is not None and routine_workout_id is not None:
                routine_workout = RoutineWorkout.query.get(routine_workout_id)
                if routine_workout:
                    routine_workout.reps = reps
                    routine_workout.sets = sets
                    db.session.commit()
                    flash('Workout updated successfully.', 'success')
                else:
                    flash('Could not find the specified workout in the routine.', 'error')
            else:
                flash('Invalid input for updating workout.', 'error')
            return redirect(request.referrer or url_for('auth_views.home_page'))

        routine_id = request.form.get('routine_id')
        if 'workout_id' in request.form:
            workout_id = request.form.get('workout_id')
            reps = request.form.get('reps', type=int)
            sets = request.form.get('sets', type=int)

            if not reps or not sets or not routine_id:
                flash('Please ensure all fields are filled out correctly. Reps and Sets must be above 0, and a Routine must be selected.', 'error')
                return redirect(request.referrer or url_for('auth_views.home_page', workout_id=workout_id))
            else:
                if RoutineWorkout.query.filter_by(routine_id=routine_id, workout_id=workout_id).first():
                    flash('Workout already exists in this routine.', 'warning')
                else:
                    routine_workout = RoutineWorkout(routine_id=routine_id, workout_id=workout_id, reps=reps, sets=sets)
                    db.session.add(routine_workout)
                    db.session.commit()
                    flash('Workout added to routine successfully.', 'success')
            return redirect(request.referrer or url_for('auth_views.home_page'))

        elif 'routine_title' in request.form:
            # Handle creating routine
            routine_title = request.form.get('routine_title')
            # Ensures a user enters 1 or more character(s) for routine title
            if not routine_title:
                flash('Routine title is required.', 'danger')
                return redirect(request.referrer or url_for('auth_views.home_page'))
            existing_routine = Routine.query.filter_by(title=routine_title, user_id=current_user.id).first()
            if existing_routine:
                flash('Routine with the same title already exists.', 'danger')
            else:
                new_routine = Routine(title=routine_title, user_id=current_user.id)
                db.session.add(new_routine)
                db.session.commit()
                flash('Routine created successfully.', 'success')
            return redirect(request.referrer or url_for('auth_views.home_page'))

    if search_query:
        workouts = Workout.query.filter(Workout.title.ilike(f'%{search_query}%')).all()
        if not workouts:
            flash('No workouts found for the search query.', 'warning')
    else:
        workout_id = request.args.get('workout_id', type=int)
        if workout_id:
            selected_workout = Workout.query.get_or_404(workout_id)
        workouts = Workout.query.all()

    routine_id = request.args.get('routine_id', type=int)
    
    if routine_id:
        selected_routine = Routine.query.get_or_404(routine_id)

    return render_template('home.html', workouts=workouts, selected_workout=selected_workout, user_routines=user_routines, selected_routine=selected_routine, is_authenticated=True)



@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({'message': f"username: {current_user.username}, id : {current_user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/', defaults={'path': ''})
@auth_views.route('/<path:path>')
def catch_all(path):
    return redirect(url_for('auth_views.home_page'))