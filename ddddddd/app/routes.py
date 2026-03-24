from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_socketio import join_room, emit

from app import db
from app.models import (
    User, UserPhoto, Restaurant, Booking,
    CompanionRequest, Message, Review, RestaurantLike
)
from app.forms import (
    ProfileForm, BookingForm, ReviewForm,
    CompanionRequestForm, MessageForm
)
from app.services import seed_initial_data, finish_meeting_request, reject_other_requests_for_booking
from app.utils import save_uploaded_file, average_rating

main = Blueprint('main', __name__)


@main.route('/init-db')
def init_db():
    seed_initial_data()
    return 'База данных создана. Админ: admin@tablemeet.ru / admin123'


@main.route('/')
def index():
    restaurants = Restaurant.query.limit(6).all()
    companion_bookings = Booking.query.filter_by(need_companion=True, status='active').limit(6).all()
    return render_template('index.html', restaurants=restaurants, companion_bookings=companion_bookings, average_rating=average_rating)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    if request.method == 'GET':
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.age.data = current_user.age
        form.gender.data = current_user.gender
        form.about.data = current_user.about

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.age = form.age.data
        current_user.gender = form.gender.data
        current_user.about = form.about.data

        avatar_file = request.files.get('avatar')
        avatar_name = save_uploaded_file(avatar_file)
        if avatar_name:
            current_user.avatar = avatar_name

        photos = request.files.getlist('photos')
        for file_obj in photos:
            filename = save_uploaded_file(file_obj)
            if filename:
                db.session.add(UserPhoto(filename=filename, user_id=current_user.id))

        db.session.commit()
        flash('Профиль обновлён')
        return redirect(url_for('main.profile'))

    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    favorite_restaurants = [like.restaurant for like in current_user.likes]
    return render_template(
        'profile.html',
        form=form,
        bookings=bookings,
        favorite_restaurants=favorite_restaurants,
        average_rating=average_rating
    )


@main.route('/user/<int:user_id>')
@login_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_detail.html', user=user)


@main.route('/delete-user-photo/<int:photo_id>')
@login_required
def delete_user_photo(photo_id):
    photo = UserPhoto.query.get_or_404(photo_id)
    if photo.user_id != current_user.id:
        abort(403)

    db.session.delete(photo)
    db.session.commit()
    flash('Фото удалено')
    return redirect(url_for('main.profile'))


@main.route('/restaurants')
def restaurants():
    search = request.args.get('search', '').strip()
    cuisine = request.args.get('cuisine', '').strip()

    query = Restaurant.query
    if search:
        query = query.filter(Restaurant.name.ilike(f'%{search}%'))
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(f'%{cuisine}%'))

    restaurants = query.all()

    map_data = [
        {
            'id': r.id,
            'name': r.name,
            'lat': r.latitude,
            'lng': r.longitude,
            'address': r.address
        }
        for r in restaurants if r.latitude and r.longitude
    ]

    return render_template('restaurants.html', restaurants=restaurants, map_data=map_data, average_rating=average_rating)


@main.route('/restaurant/<int:restaurant_id>', methods=['GET', 'POST'])
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    review_form = ReviewForm()

    if review_form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            user_id=current_user.id,
            restaurant_id=restaurant.id,
            rating=int(review_form.rating.data),
            text=review_form.text.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Отзыв добавлен')
        return redirect(url_for('main.restaurant_detail', restaurant_id=restaurant.id))

    likes_count = RestaurantLike.query.filter_by(restaurant_id=restaurant.id).count()
    user_liked = False
    if current_user.is_authenticated:
        user_liked = RestaurantLike.query.filter_by(
            user_id=current_user.id,
            restaurant_id=restaurant.id
        ).first() is not None

    reviews = Review.query.filter_by(restaurant_id=restaurant.id).order_by(Review.created_at.desc()).all()

    return render_template(
        'restaurant_detail.html',
        restaurant=restaurant,
        review_form=review_form,
        likes_count=likes_count,
        user_liked=user_liked,
        reviews=reviews,
        avg_rating=average_rating(restaurant)
    )


@main.route('/restaurant/<int:restaurant_id>/like')
@login_required
def like_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    existing = RestaurantLike.query.filter_by(user_id=current_user.id, restaurant_id=restaurant.id).first()

    if existing:
        db.session.delete(existing)
        flash('Лайк убран')
    else:
        db.session.add(RestaurantLike(user_id=current_user.id, restaurant_id=restaurant.id))
        flash('Ресторан добавлен в избранное')

    db.session.commit()
    return redirect(url_for('main.restaurant_detail', restaurant_id=restaurant.id))


@main.route('/booking/<int:restaurant_id>', methods=['GET', 'POST'])
@login_required
def create_booking(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = BookingForm()

    if form.validate_on_submit():
        guests = int(form.guests.data)
        need_companion = guests == 1 and form.need_companion.data == 'yes'

        booking = Booking(
            user_id=current_user.id,
            restaurant_id=restaurant.id,
            booking_date=form.booking_date.data,
            booking_time=form.booking_time.data,
            guests=guests,
            comment=form.comment.data,
            need_companion=need_companion,
            preferred_gender=form.preferred_gender.data or None,
            preferred_age_min=form.preferred_age_min.data,
            preferred_age_max=form.preferred_age_max.data,
            companion_comment=form.companion_comment.data
        )
        db.session.add(booking)
        db.session.commit()
        flash('Бронь создана')
        return redirect(url_for('main.profile'))

    return render_template('booking_form.html', form=form, restaurant=restaurant)


@main.route('/booking/<int:booking_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)

    form = BookingForm()

    if request.method == 'GET':
        form.booking_date.data = booking.booking_date
        form.booking_time.data = booking.booking_time
        form.guests.data = str(booking.guests)
        form.need_companion.data = 'yes' if booking.need_companion else 'no'
        form.preferred_gender.data = booking.preferred_gender or ''
        form.preferred_age_min.data = booking.preferred_age_min
        form.preferred_age_max.data = booking.preferred_age_max
        form.companion_comment.data = booking.companion_comment
        form.comment.data = booking.comment

    if form.validate_on_submit():
        booking.booking_date = form.booking_date.data
        booking.booking_time = form.booking_time.data
        booking.guests = int(form.guests.data)
        booking.comment = form.comment.data

        if booking.guests == 1 and form.need_companion.data == 'yes':
            booking.need_companion = True
            booking.preferred_gender = form.preferred_gender.data or None
            booking.preferred_age_min = form.preferred_age_min.data
            booking.preferred_age_max = form.preferred_age_max.data
            booking.companion_comment = form.companion_comment.data
        else:
            booking.need_companion = False
            booking.preferred_gender = None
            booking.preferred_age_min = None
            booking.preferred_age_max = None
            booking.companion_comment = None

        db.session.commit()
        flash('Бронь обновлена')
        return redirect(url_for('main.profile'))

    return render_template('edit_booking.html', form=form, booking=booking)


@main.route('/booking/<int:booking_id>/delete')
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)

    db.session.delete(booking)
    db.session.commit()
    flash('Бронь удалена')
    return redirect(url_for('main.profile'))


@main.route('/companions', methods=['GET', 'POST'])
def companions():
    gender = request.args.get('gender', '').strip()
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)

    bookings = Booking.query.filter_by(need_companion=True, status='active').order_by(Booking.created_at.desc()).all()
    filtered = []

    for booking in bookings:
        user = booking.user
        if gender and gender != 'Не важно' and user.gender != gender:
            continue
        if age_min is not None:
            if user.age is None or user.age < age_min:
                continue
        if age_max is not None:
            if user.age is None or user.age > age_max:
                continue
        filtered.append(booking)

    form = CompanionRequestForm()
    return render_template('companions.html', bookings=filtered, form=form)


@main.route('/companion-request/<int:booking_id>', methods=['POST'])
@login_required
def companion_request(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    form = CompanionRequestForm()

    if booking.user_id == current_user.id:
        flash('Нельзя отправить запрос самому себе')
        return redirect(url_for('main.companions'))

    if form.validate_on_submit():
        existing = CompanionRequest.query.filter_by(
            booking_id=booking.id,
            from_user_id=current_user.id,
            status='pending'
        ).first()

        if existing:
            flash('Вы уже отправили запрос')
            return redirect(url_for('main.companions'))

        req = CompanionRequest(
            booking_id=booking.id,
            from_user_id=current_user.id,
            to_user_id=booking.user_id,
            message=form.message.data,
            status='pending'
        )
        db.session.add(req)
        db.session.commit()
        flash('Запрос отправлен')

    return redirect(url_for('main.companions'))


@main.route('/my-requests')
@login_required
def my_requests():
    received = CompanionRequest.query.filter_by(to_user_id=current_user.id).order_by(CompanionRequest.created_at.desc()).all()
    sent = CompanionRequest.query.filter_by(from_user_id=current_user.id).order_by(CompanionRequest.created_at.desc()).all()
    return render_template('my_requests.html', received=received, sent=sent)


@main.route('/request/<int:request_id>/accept')
@login_required
def accept_request(request_id):
    req = CompanionRequest.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        abort(403)

    req.status = 'accepted'
    req.booking.status = 'closed'
    db.session.commit()

    reject_other_requests_for_booking(req)
    flash('Запрос принят')
    return redirect(url_for('main.my_requests'))


@main.route('/request/<int:request_id>/reject')
@login_required
def reject_request(request_id):
    req = CompanionRequest.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        abort(403)

    req.status = 'rejected'
    db.session.commit()
    flash('Запрос отклонён')
    return redirect(url_for('main.my_requests'))


@main.route('/request/<int:request_id>/cancel')
@login_required
def cancel_request(request_id):
    req = CompanionRequest.query.get_or_404(request_id)
    if req.from_user_id != current_user.id:
        abort(403)

    req.status = 'cancelled'
    db.session.commit()
    flash('Заявка отменена')
    return redirect(url_for('main.my_requests'))


@main.route('/request/<int:request_id>/finish')
@login_required
def finish_request(request_id):
    req = CompanionRequest.query.get_or_404(request_id)

    if current_user.id not in [req.from_user_id, req.to_user_id]:
        abort(403)

    if req.status != 'accepted':
        flash('Завершить можно только принятую встречу')
        return redirect(url_for('main.my_meetings'))

    finish_meeting_request(req)
    flash('Встреча завершена')
    return redirect(url_for('main.my_meetings'))


@main.route('/my-meetings')
@login_required
def my_meetings():
    meetings = CompanionRequest.query.filter(
        ((CompanionRequest.from_user_id == current_user.id) | (CompanionRequest.to_user_id == current_user.id)),
        CompanionRequest.status.in_(['accepted', 'finished'])
    ).order_by(CompanionRequest.created_at.desc()).all()

    return render_template('my_meetings.html', meetings=meetings)


@main.route('/chat/<int:user_id>')
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user.id)) |
        ((Message.sender_id == other_user.id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()

    room_name = '_'.join(map(str, sorted([current_user.id, other_user.id])))
    form = MessageForm()
    return render_template('chat.html', other_user=other_user, messages=messages, room_name=room_name, form=form)


def register_socket_events(socketio_instance):
    @socketio_instance.on('join')
    def on_join(data):
        room = data['room']
        join_room(room)

    @socketio_instance.on('send_message')
    def handle_send_message(data):
        sender_id = int(data['sender_id'])
        receiver_id = int(data['receiver_id'])
        text = data['text'].strip()
        room = data['room']

        if not text:
            return

        msg = Message(sender_id=sender_id, receiver_id=receiver_id, text=text)
        db.session.add(msg)
        db.session.commit()

        emit('receive_message', {
            'sender_id': sender_id,
            'text': text,
            'sender_name': data.get('sender_name', 'Пользователь')
        }, to=room)