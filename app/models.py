from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('docente.id_docente'), nullable=True)

class DOCENTE(UserMixin, db.Model):
    __tablename__ = 'docente'
    id_docente = db.Column(db.Integer, primary_key=True)
    rut_docente = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    contraseña = db.Column(db.String(150))
    activo = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='docente', lazy=True)

class Sala(db.Model):
    id_sala = db.Column(db.Integer, primary_key=True)
    nombre_sala = db.Column(db.String(50), nullable=False)

class Taller(db.Model):
    taller_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    id_sala = db.Column(db.Integer, db.ForeignKey('sala.id_sala'), nullable=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('docente.id_docente'), nullable=False)

    sala = db.relationship('Sala', backref=db.backref('talleres', lazy=True))
    docente = db.relationship('DOCENTE', backref=db.backref('talleres', lazy=True))
    estudiantes_taller = db.relationship('EstudianteTaller', backref='taller', lazy=True)
    clases = db.relationship('Clase', back_populates='taller')

class Estudiantes(db.Model):
    id_estudiante = db.Column(db.Integer, primary_key=True)
    rut_estudiante = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50), nullable=False)
    curso = db.Column(db.String(20))
    correo_institucional = db.Column(db.String(100))

    talleres = db.relationship('EstudianteTaller', backref='estudiante', lazy=True)

class EstudianteTaller(db.Model):
    id_taller_estudiante = db.Column(db.Integer, primary_key=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey('estudiantes.id_estudiante'), nullable=False)
    taller_id = db.Column(db.Integer, db.ForeignKey('taller.taller_id'), nullable=False)

class Clase(db.Model):
    __tablename__ = 'clase'
    
    id_clase = db.Column(db.Integer, primary_key=True)
    taller_id = db.Column(db.Integer, db.ForeignKey('taller.taller_id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    comentario_bitacora = db.Column(db.Text, nullable=True)
    
    taller = db.relationship('Taller', back_populates='clases')

class AsistenciaEstudiante(db.Model):
    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase'), nullable=False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey('estudiantes.id_estudiante'), nullable=False)
    presencia = db.Column(db.Boolean, nullable=False)
    justificacion = db.Column(db.Text)

    clase = db.relationship('Clase', backref=db.backref('asistencias', lazy=True))
    estudiante = db.relationship('Estudiantes', backref=db.backref('asistencias', lazy=True))
