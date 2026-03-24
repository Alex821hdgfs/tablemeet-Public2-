from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required
from app import db
from app.decorators import admin_required
from app.forms import RestaurantForm
from app.models import User, Restaurant, Booking, RestaurantPhoto
from app.utils import save_uploaded_file

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    restaurants = Restaurant.query.all()
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin.html', users=users, restaurants=restaurants, bookings=bookings)


@admin_bp.route('/add-restaurant', methods=['GET', 'POST'])
@login_required
@admin_required
def add_restaurant():
    form = RestaurantForm()
    if form.validate_on_submit():
        image_name = save_uploaded_file(request.files.get('image'))

        restaurant = Restaurant(
            name=form.name.data,
            cuisine=form.cuisine.data,
            address=form.address.data,
            description=form.description.data,
            average_check=form.average_check.data,
            menu=form.menu.data,
            latitude=float(form.latitude.data) if form.latitude.data else None,
            longitude=float(form.longitude.data) if form.longitude.data else None,
            image=image_name
        )
        db.session.add(restaurant)
        db.session.commit()

        photos = request.files.getlist('photos')
        for file_obj in photos:
            filename = save_uploaded_file(file_obj)
            if filename:
                db.session.add(RestaurantPhoto(filename=filename, restaurant_id=restaurant.id))

        db.session.commit()
        flash('Ресторан добавлен')
        return redirect(url_for('admin.dashboard'))

    return render_template('add_restaurant.html', form=form)


@admin_bp.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = RestaurantForm()

    if request.method == 'GET':
        form.name.data = restaurant.name
        form.cuisine.data = restaurant.cuisine
        form.address.data = restaurant.address
        form.description.data = restaurant.description
        form.average_check.data = restaurant.average_check
        form.menu.data = restaurant.menu
        form.latitude.data = restaurant.latitude
        form.longitude.data = restaurant.longitude

    if form.validate_on_submit():
        restaurant.name = form.name.data
        restaurant.cuisine = form.cuisine.data
        restaurant.address = form.address.data
        restaurant.description = form.description.data
        restaurant.average_check = form.average_check.data
        restaurant.menu = form.menu.data
        restaurant.latitude = float(form.latitude.data) if form.latitude.data else None
        restaurant.longitude = float(form.longitude.data) if form.longitude.data else None

        image_name = save_uploaded_file(request.files.get('image'))
        if image_name:
            restaurant.image = image_name

        photos = request.files.getlist('photos')
        for file_obj in photos:
            filename = save_uploaded_file(file_obj)
            if filename:
                db.session.add(RestaurantPhoto(filename=filename, restaurant_id=restaurant.id))

        db.session.commit()
        flash('Ресторан обновлён')
        return redirect(url_for('admin.dashboard'))

    return render_template('edit_restaurant.html', form=form, restaurant=restaurant)


@admin_bp.route('/restaurant-photo/<int:photo_id>/delete')
@login_required
@admin_required
def delete_restaurant_photo(photo_id):
    photo = RestaurantPhoto.query.get_or_404(photo_id)
    db.session.delete(photo)
    db.session.commit()
    flash('Фото ресторана удалено')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/restaurant/<int:restaurant_id>/delete')
@login_required
@admin_required
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    db.session.delete(restaurant)
    db.session.commit()
    flash('Ресторан удалён')
    return redirect(url_for('admin.dashboard'))