# __init__.py (เฉพาะส่วนสำคัญ)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('project.config.Config')

    # Init extensions
    db.init_app(app)
    socketio.init_app(app, async_mode='eventlet')
    login_manager.init_app(app)
    Migrate(app, db)
    CORS(app)

    # Register blueprints
    from routes.main import main_bp
    from routes.api import api_bp
    from routes.admin import admin_bp
    from routes.chat import chat_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/chat')

    # Register Socket.IO namespaces
    from sockets import register_socketio_namespaces
    register_socketio_namespaces(socketio)

    return app
if __name__ == '__main__':
    socketio.run(host='0.0.0.0', port=1338)
