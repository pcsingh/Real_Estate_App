from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (StringField, PasswordField, SubmitField, 
					SelectField, BooleanField, TextAreaField, IntegerField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from real_estate_app.models import User, House

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	name = StringField('Full Name', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
	user_type = SelectField('User Type', choices=[('admin', 'Admin'), ('agent', 'Agent')], validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', 
									validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
	# username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	# name = StringField('Full Name', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	# gender = SelectField('Gender', choices=[('m', 'Male'), ('f', 'Female')], validators=[DataRequired()])
	user_type = SelectField('User Type', choices=[('admin', 'Admin'), ('agent', 'Agent')], validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	name = StringField('Full Name', validators=[DataRequired()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')

class HouseForm(FlaskForm):
	name = StringField('Name of House:', validators=[DataRequired()])
	price = IntegerField('Price in Lakh:', validators=[NumberRange(min=0, max=500)])
	house_type = StringField('Type of House:', validators=[DataRequired()])
	picture = FileField('Upload House Image', validators=[FileAllowed(['jpg', 'png'])])
	description = TextAreaField('About House:', validators=[DataRequired()], render_kw={"placeholder": "Ex: Address and other details."})
	submit = SubmitField('Add House')


class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('There is no account with that email, You need to register first.')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', 
					validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Reset Password')

