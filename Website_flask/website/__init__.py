import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import make_url
from flask_login import LoginManager


login_manager = LoginManager()
db = SQLAlchemy()
DB_NAME = "postgresql://postgres:azerty@localhost:5433/cookbooked_db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'nata password'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_NAME
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .follow import follow
    from .models import User

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(follow, url_prefix='/')

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    db_url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
    database_name = db_url.database

    conn = psycopg2.connect(
        host=db_url.host,
        port=db_url.port,
        user=db_url.username,
        password=db_url.password
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {database_name}")
            print(f"Created PostgreSQL Database: {database_name}")
    except Exception as e:
        print(f"Error checking/creating database: {e}")
    finally:
        cursor.close()
        conn.close()

    with app.app_context():
        db.create_all()
        print('Created Tables')