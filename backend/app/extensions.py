from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate(compare_type=True)
jwt = JWTManager()
cors = CORS()
token_blocklist = set()
