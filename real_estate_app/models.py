from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from real_estate_app import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	name = db.Column(db.String(60), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	gender = db.Column(db.String(20), nullable=False)
	user_type = db.Column(db.String(20),  nullable=False)
	user_image = db.Column(db.String(20), nullable=False, default='user.jpg')
	password = db.Column(db.String(60), nullable=False)
	houses = db.relationship('House', backref='owner', lazy=True)

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"""User('{self.id}', '{self.username}', '{self.name}', '{self.email}', 
			'{self.gender}', '{self.user_type}', '{self.user_image}')"""


class House(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	house_type = db.Column(db.String(100), nullable=False)
	date_added = db.Column(db.DateTime, nullable=False, default=datetime.today)
	house_image = db.Column(db.String(20), nullable=False, default='house.jpg')
	description = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"""House('{self.id}', '{self.name}', '{self.price}', '{self.house_type}', 
				'{self.date_added}', '{self.description}', '{self.house_image}', '{self.user_id}')"""

