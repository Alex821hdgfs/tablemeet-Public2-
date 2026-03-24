from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Restaurant, CompanionRequest


def seed_initial_data():
    if not User.query.filter_by(email='admin@tablemeet.ru').first():
        admin = User(
            name='Администратор',
            email='admin@tablemeet.ru',
            phone='+70000000000',
            is_admin=True,
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)

    if Restaurant.query.count() == 0:
        db.session.add_all([
            Restaurant(
                name='La Piazza',
                cuisine='Итальянская кухня',
                address='Москва, ул. Пушкина, 10',
                description='Уютный итальянский ресторан.',
                average_check=1500,
                menu='Пицца, паста, десерты',
                latitude=55.7558,
                longitude=37.6173
            ),
            Restaurant(
                name='Sushi Point',
                cuisine='Японская кухня',
                address='Москва, ул. Арбат, 5',
                description='Свежие роллы и суши.',
                average_check=1200,
                menu='Роллы, суши, супы',
                latitude=55.7520,
                longitude=37.5920
            ),
            Restaurant(
                name='BBQ House',
                cuisine='Американская кухня',
                address='Москва, пр. Мира, 20',
                description='Стейки и гриль.',
                average_check=1800,
                menu='Стейки, бургеры, BBQ',
                latitude=55.7810,
                longitude=37.6330
            )
        ])

    db.session.commit()


def finish_meeting_request(req):
    req.status = 'finished'
    req.booking.status = 'completed'
    db.session.commit()


def reject_other_requests_for_booking(accepted_request):
    others = CompanionRequest.query.filter(
        CompanionRequest.booking_id == accepted_request.booking_id,
        CompanionRequest.id != accepted_request.id,
        CompanionRequest.status == 'pending'
    ).all()

    for item in others:
        item.status = 'rejected'

    db.session.commit()