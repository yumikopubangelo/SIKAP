from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_name=None):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Configure Flask app
    if config_name == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'mysql+pymysql://user:password@db:3306/sikap'
        )
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    else:
        # Development configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'mysql+pymysql://root:password@localhost:3306/sikap'
        )
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        # TODO: Uncomment when models are implemented
        # from app.models import (
        #     user, guru, siswa, orangtua, kelas, 
        #     absensi, audit_log, notifikasi, 
        #     perangkat, sekolah, surat_peringatan, waktu_sholat
        # )
        
        # Register route blueprints
        # TODO: Uncomment when routes are implemented
        # from app.routes import (
        #     auth, users, siswa as siswa_routes,
        #     kelas as kelas_routes,
        #     absensi as absensi_routes, laporan, rekapitulasi,
        #     notifikasi as notifikasi_routes, perangkat as perangkat_routes,
        #     sekolah as sekolah_routes, surat_peringatan as sp_routes,
        #     waktu_sholat as waktu_sholat_routes
        # )
        
        # TODO: Register blueprints if they are defined
        # Uncomment as blueprints are implemented
        # app.register_blueprint(auth.bp)
        # app.register_blueprint(users.bp)
        # app.register_blueprint(siswa_routes.bp)
        # etc...
        pass
    
    return app