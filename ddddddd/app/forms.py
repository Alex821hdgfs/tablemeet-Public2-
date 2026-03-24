from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField, FileField
from wtforms.validators import DataRequired, Email, Optional


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[Optional()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[Optional()])
    age = IntegerField('Возраст', validators=[Optional()])
    gender = SelectField('Пол', choices=[
        ('', 'Не выбрано'),
        ('Мужчина', 'Мужчина'),
        ('Женщина', 'Женщина')
    ])
    about = TextAreaField('О себе', validators=[Optional()])
    avatar = FileField('Аватар')
    submit = SubmitField('Сохранить')


class BookingForm(FlaskForm):
    booking_date = StringField('Дата', validators=[DataRequired()])
    booking_time = StringField('Время', validators=[DataRequired()])
    guests = SelectField('Количество гостей', choices=[
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4+')
    ])
    need_companion = SelectField('Подобрать компанию?', choices=[
        ('no', 'Нет'),
        ('yes', 'Да')
    ])
    preferred_gender = SelectField('Пол компаньона', choices=[
        ('', 'Не важно'),
        ('Мужчина', 'Мужчина'),
        ('Женщина', 'Женщина')
    ])
    preferred_age_min = IntegerField('Возраст от', validators=[Optional()])
    preferred_age_max = IntegerField('Возраст до', validators=[Optional()])
    companion_comment = TextAreaField('Комментарий для компании', validators=[Optional()])
    comment = TextAreaField('Комментарий к брони', validators=[Optional()])
    submit = SubmitField('Сохранить бронь')


class RestaurantForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    cuisine = StringField('Кухня', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Optional()])
    average_check = IntegerField('Средний чек', validators=[Optional()])
    menu = TextAreaField('Меню', validators=[Optional()])
    latitude = StringField('Широта', validators=[Optional()])
    longitude = StringField('Долгота', validators=[Optional()])
    image = FileField('Главное фото')
    submit = SubmitField('Сохранить ресторан')


class ReviewForm(FlaskForm):
    rating = SelectField('Оценка', choices=[
        ('5', '5'),
        ('4', '4'),
        ('3', '3'),
        ('2', '2'),
        ('1', '1')
    ])
    text = TextAreaField('Отзыв', validators=[Optional()])
    submit = SubmitField('Оставить отзыв')


class MessageForm(FlaskForm):
    text = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class CompanionRequestForm(FlaskForm):
    message = TextAreaField('Сообщение', validators=[Optional()])
    submit = SubmitField('Присоединиться')

