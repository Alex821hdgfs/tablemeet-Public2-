from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30))
    password_hash = db.Column(db.String(255), nullable=False)

    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    about = db.Column(db.Text)
    avatar = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

    bookings = db.relationship('Booking', backref='user', lazy=True, cascade='all, delete-orphan')
    profile_photos = db.relationship('UserPhoto', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='author', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('RestaurantLike', backref='user', lazy=True, cascade='all, delete-orphan')

    sent_requests = db.relationship(
        'CompanionRequest',
        foreign_keys='CompanionRequest.from_user_id',
        backref='from_user',
        lazy=True,
        cascade='all, delete-orphan'
    )
    received_requests = db.relationship(
        'CompanionRequest',
        foreign_keys='CompanionRequest.to_user_id',
        backref='to_user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    sent_messages = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        backref='sender',
        lazy=True,
        cascade='all, delete-orphan'
    )
    received_messages = db.relationship(
        'Message',
        foreign_keys='Message.receiver_id',
        backref='receiver',
        lazy=True,
        cascade='all, delete-orphan'
    )


class UserPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    average_check = db.Column(db.Integer)
    menu = db.Column(db.Text)
    image = db.Column(db.String(255))

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    bookings = db.relationship('Booking', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('RestaurantPhoto', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('RestaurantLike', backref='restaurant', lazy=True, cascade='all, delete-orphan')


class RestaurantPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    booking_date = db.Column(db.String(50), nullable=False)
    booking_time = db.Column(db.String(50), nullable=False)
    guests = db.Column(db.Integer, nullable=False, default=1)
    comment = db.Column(db.Text)

    need_companion = db.Column(db.Boolean, default=False)
    preferred_gender = db.Column(db.String(20))
    preferred_age_min = db.Column(db.Integer)
    preferred_age_max = db.Column(db.Integer)
    companion_comment = db.Column(db.Text)

    status = db.Column(db.String(20), default='active')  # active / closed / cancelled / completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship('CompanionRequest', backref='booking', lazy=True, cascade='all, delete-orphan')


class CompanionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending / accepted / rejected / cancelled / finished
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RestaurantLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))