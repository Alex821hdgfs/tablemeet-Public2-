import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
socketio = SocketIO(async_mode='eventlet')


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    from app.auth_routes import auth
    from app.routes import main
    from app.admin_routes import admin_bp

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin_bp)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error_403.html'), 403

    with app.app_context():
        db.create_all()

    from app.routes import register_socket_events
    register_socket_events(socketio)

    return app