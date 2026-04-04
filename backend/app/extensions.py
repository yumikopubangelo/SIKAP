from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Initialize extensions (without app)
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
