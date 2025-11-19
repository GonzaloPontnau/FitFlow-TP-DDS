from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# db is already in src/config/database.py, so we won't put it here to avoid refactoring everything
# But for new extensions:

socketio = SocketIO(cors_allowed_origins="*")
limiter = Limiter(key_func=get_remote_address)
