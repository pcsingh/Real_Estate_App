import os
import secrets
from PIL import Image
from flask import url_for, current_app
import sendgrid
from sendgrid.helpers.mail import *
from real_estate_app import app, sg


def save_user_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/images/profile_pics', picture_fn)
	
	output_size = (512, 512)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn

def save_house_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)

	output_size = (512, 512)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


def send_reset_email(user):
	token = user.get_reset_token()
	from_email = Email('noreply@sellandbuy.com')
	to_email = To(user.email)
	subject = 'Password Reset Request'
	msg = f'''
	To reset your password, visit the following link:
	</br>
	<a href="{ url_for('reset_token', token=token, _external=True) }">Click here.</a>
	</br>
	</br>
	If you do not make this request then simply ignore this email and no changes will be made.
	'''
	content = Content('text/html', msg)
	mail = Mail(from_email, to_email, subject, content)
	response = sg.client.mail.send.post(request_body=mail.get())

