from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User
from app.forms import RegisterForm, LoginForm

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('Пользователь с таким email уже существует')
            return redirect(url_for('auth.register'))

        user = User(
            name=form.name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Вы вошли в аккаунт')
            return redirect(url_for('main.index'))
        flash('Неверный email или пароль')
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из аккаунта')
    return redirect(url_for('main.index'))