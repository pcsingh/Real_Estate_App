import os
import secrets
from real_estate_app.utils import save_user_picture, save_house_picture, send_reset_email
from flask import render_template, url_for, flash, redirect, request, abort
from real_estate_app import app, db, bcrypt
from real_estate_app.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
								HouseForm, RequestResetForm, ResetPasswordForm)
from real_estate_app.models import User, House
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
	page = request.args.get('page', 1, type=int)
	houses = House.query.order_by(House.date_added.desc()).paginate(page=page, per_page=6)
	return render_template('home.html', houses=houses)

@app.route('/about')
def about():
	return render_template('about.html', title='About')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data) and user.user_type == form.user_type.data:
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please enter correct credentials.', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, name=form.name.data, email=form.email.data, gender=form.gender.data, user_type=form.user_type.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created! You are now able to log in.', 'success')
		return redirect(url_for('home'))
	return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
	logout_user()
	flash(f'Logged out successfully.', 'success')
	return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_user_picture(form.picture.data)
			current_user.user_image = picture_file
		current_user.username = form.username.data
		current_user.name = form.name.data
		db.session.commit()
		flash(f'Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.name.data = current_user.name
	user_image = url_for('static', filename='images/profile_pics/'+current_user.user_image)
	return render_template('account.html', title='Account', user_image=user_image, form=form)

@app.route("/house/new", methods=['GET', 'POST'])
@login_required
def new_house():
	if current_user.user_type != 'admin':
		abort(403)
	form = HouseForm()
	if form.validate_on_submit():
		house_image = 'house.jpg'
		if form.picture.data:
			picture_file = save_house_picture(form.picture.data)
			house_image = picture_file
		house = House(name=form.name.data, house_type=form.house_type.data, description=form.description.data, price=form.price.data, owner=current_user, house_image=house_image)
		db.session.add(house)
		db.session.commit()
		flash('New house has been added!', 'success')
		return redirect(url_for('home'))
	return render_template('add_house.html', title='Add House', form=form, legend='New House')

@app.route("/house/<int:house_id>")
def house(house_id):
	house = House.query.get_or_404(house_id)
	return render_template('house.html', title=house.name, house=house)

@app.route("/house/<int:house_id>/update", methods=['GET', 'POST'])
@login_required
def update_house(house_id):
	house = House.query.get_or_404(house_id)
	if house.owner != current_user:
		abort(403)
	form = HouseForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_house_picture(form.picture.data)
			house.house_image = picture_file
		house.name = form.name.data
		house.price = form.price.data
		house.house_type = form.house_type.data
		house.description = form.description.data
		db.session.commit()
		flash('Your house has been updated!', 'success')
		return redirect(url_for('house', house_id=house.id))
	elif request.method == 'GET':
		form.name.data = house.name
		form.price.data = house.price
		form.house_type.data = house.house_type
		form.description.data = house.description
	house_image = url_for('static', filename='images/'+house.house_image)
	return render_template('update_house.html', title='Update', form=form, house_image=house_image, legend='Update House')

@app.route("/house/<int:house_id>/delete", methods=['POST'])
@login_required
def delete_house(house_id):
	house = House.query.get_or_404(house_id)
	if house.owner != current_user:
		abort(403)
	db.session.delete(house)
	db.session.commit()
	flash(f'Your house has been deleted!', 'success')
	return redirect(url_for('home'))

# @app.route("/user/<string:username>")
# @login_required
# def user_posts(username):
# 	page = request.args.get('page', 1, type=int)
# 	user = User.query.filter_by(username=username).first_or_404()
# 	houses = House.query.filter_by(owner=user).order_by(House.date_added.desc())\
# 			.paginate(page=page, per_page=6)
# 	return render_template('admin_addedhouse.html', houses=houses, user=user)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with further instructions.', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.errorhandler(404)
def error_404(error):
	return render_template('errors/404.html'), 404

@app.errorhandler(403)
def error_403(error):
	return render_template('errors/403.html'), 403

@app.errorhandler(500)
def error_500(error):
	return render_template('errors/500.html'), 500

