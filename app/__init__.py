from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from .extensions import db, login_manager
from .models import User

conection = "mysql+pymysql://admin:pqOeuFLP0WvmSsqOXesI@database-catemuacles.cbq4sgyai27e.us-east-2.rds.amazonaws.com/prueba_1"

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = conection
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.docentes import docentes_bp
    from app.routes.salas import salas_bp
    from app.routes.talleres import talleres_bp
    from app.routes.estudiantes import estudiantes_bp
    from app.routes.clases import clases_bp
    from app.routes.estudiantes_taller import estudiantes_taller_bp
    from app.routes.asistencias import asistencias_bp
    from app.routes.bitacoras import bitacoras_bp
    from app.routes.docente import docente_bp  # Actualiza esta línea
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(docentes_bp, url_prefix='/docentes')
    app.register_blueprint(salas_bp, url_prefix='/salas')
    app.register_blueprint(talleres_bp, url_prefix='/talleres')
    app.register_blueprint(estudiantes_bp, url_prefix='/estudiantes')
    app.register_blueprint(clases_bp, url_prefix='/clases')
    app.register_blueprint(estudiantes_taller_bp, url_prefix='/estudiantes_taller')
    app.register_blueprint(asistencias_bp, url_prefix='/asistencias')
    app.register_blueprint(bitacoras_bp, url_prefix='/bitacoras')
    app.register_blueprint(docente_bp, url_prefix='/docente')  # Actualiza esta línea
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('docente.dashboard'))  # Actualiza esta línea

    return app
