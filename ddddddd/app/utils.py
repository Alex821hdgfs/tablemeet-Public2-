import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def save_uploaded_file(file_obj):
    if file_obj and file_obj.filename:
        ext = os.path.splitext(file_obj.filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filename = secure_filename(unique_name)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(filepath)
        return filename
    return None


def average_rating(restaurant):
    reviews = restaurant.reviews
    if not reviews:
        return 0
    return round(sum(r.rating for r in reviews) / len(reviews), 1)