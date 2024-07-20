from flask import Flask, abort, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sqlalchemy import inspect
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
# Configuración de la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:1iY0U]U.ynXEas5Px~F]mwzf~05V@database-catemuacles.cbq4sgyai27e.us-east-2.rds.amazonaws.com/prueba_1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'

# Crear el directorio de carga si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de Usuario
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Modelo DOCENTE
class DOCENTE(UserMixin, db.Model):
    id_docente = db.Column(db.Integer, primary_key=True)
    rut_docente = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(100))
    contraseña = db.Column(db.String(150))  # Asegúrate de almacenar contraseñas cifradas

# Modelo Sala
class Sala(db.Model):
    id_sala = db.Column(db.Integer, primary_key=True)
    nombre_sala = db.Column(db.String(50), nullable=False)

# Modelo Taller
class Taller(db.Model):
    taller_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    horario = db.Column(db.String(50), nullable=False)
    id_sala = db.Column(db.Integer, db.ForeignKey('sala.id_sala'), nullable=False)
    id_docente = db.Column(db.Integer, db.ForeignKey('docente.id_docente'), nullable=False)

    sala = db.relationship('Sala', backref=db.backref('talleres', lazy=True))
    docente = db.relationship('DOCENTE', backref=db.backref('talleres', lazy=True))
    estudiantes_taller = db.relationship('EstudianteTaller', backref='taller', lazy=True)

# Modelo Estudiantes
class Estudiantes(db.Model):
    id_estudiante = db.Column(db.Integer, primary_key=True)
    rut_estudiante = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50), nullable=False)
    curso = db.Column(db.String(20))
    correo_institucional = db.Column(db.String(100))

    talleres = db.relationship('EstudianteTaller', backref='estudiante', lazy=True)

# Modelo Estudiante_Taller
class EstudianteTaller(db.Model):
    id_taller_estudiante = db.Column(db.Integer, primary_key=True)
    id_estudiante = db.Column(db.Integer, db.ForeignKey('estudiantes.id_estudiante'), nullable=False)
    taller_id = db.Column(db.Integer, db.ForeignKey('taller.taller_id'), nullable=False)

# Modelo Clase
class Clase(db.Model):
    id_clase = db.Column(db.Integer, primary_key=True)
    taller_id = db.Column(db.Integer, db.ForeignKey('taller.taller_id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    comentario_bitacora = db.Column(db.Text)

    taller = db.relationship('Taller', backref=db.backref('clases', lazy=True))

# Modelo Asistencia_Estudiante
class AsistenciaEstudiante(db.Model):
    id_asistencia = db.Column(db.Integer, primary_key=True)
    id_clase = db.Column(db.Integer, db.ForeignKey('clase.id_clase'), nullable=False)
    id_estudiante = db.Column(db.Integer, db.ForeignKey('estudiantes.id_estudiante'), nullable=False)
    presencia = db.Column(db.Boolean, nullable=False)
    justificacion = db.Column(db.Text)

    clase = db.relationship('Clase', backref=db.backref('asistencias', lazy=True))
    estudiante = db.relationship('Estudiantes', backref=db.backref('asistencias', lazy=True))

# Crear la base de datos y las tablas
with app.app_context():
    db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Nombre de usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    return "Bienvenido, Admin!"

# Rutas y lógica para CRUD de cada modelo
# DOCENTE CRUD
@app.route('/docentes')
@login_required
def docentes():
    docentes = DOCENTE.query.all()
    return render_template('docentes.html', docentes=docentes)

@app.route('/docente', methods=['POST'])
@login_required
def create_docente():
    rut_docente = request.form['rut_docente']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    contraseña = request.form.get('contraseña')
    
    nuevo_docente = DOCENTE(
        rut_docente=rut_docente,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        telefono=telefono,
        correo=correo,
        contraseña=generate_password_hash(contraseña)
    )
    
    db.session.add(nuevo_docente)
    db.session.commit()
    return redirect(url_for('docentes'))

@app.route('/docente/<int:id_docente>/delete', methods=['POST'])
@login_required
def delete_docente(id_docente):
    docente = DOCENTE.query.get_or_404(id_docente)
    db.session.delete(docente)
    db.session.commit()
    return redirect(url_for('docentes'))

@app.route('/docente/<int:id_docente>/edit', methods=['GET'])
@login_required
def edit_docente(id_docente):
    docente = DOCENTE.query.get_or_404(id_docente)
    return render_template('edit_docente.html', docente=docente)

@app.route('/docente/<int:id_docente>/edit', methods=['POST'])
@login_required
def update_docente(id_docente):
    docente = DOCENTE.query.get_or_404(id_docente)
    docente.rut_docente = request.form['rut_docente']
    docente.nombre = request.form['nombre']
    docente.apellido_paterno = request.form['apellido_paterno']
    docente.apellido_materno = request.form['apellido_materno']
    docente.telefono = request.form.get('telefono')
    docente.correo = request.form.get('correo')
    docente.contraseña = generate_password_hash(request.form.get('contraseña'))
    
    db.session.commit()
    return redirect(url_for('docentes'))

# Sala CRUD
@app.route('/salas')
@login_required
def salas():
    salas = Sala.query.all()
    return render_template('salas.html', salas=salas)

@app.route('/sala', methods=['POST'])
@login_required
def create_sala():
    nombre_sala = request.form['nombre_sala']
    nueva_sala = Sala(nombre_sala=nombre_sala)
    db.session.add(nueva_sala)
    db.session.commit()
    return redirect(url_for('salas'))

@app.route('/sala/<int:id_sala>/delete', methods=['POST'])
@login_required
def delete_sala(id_sala):
    sala = Sala.query.get_or_404(id_sala)
    db.session.delete(sala)
    db.session.commit()
    return redirect(url_for('salas'))

@app.route('/sala/<int:id_sala>/edit', methods=['GET'])
@login_required
def edit_sala(id_sala):
    sala = Sala.query.get_or_404(id_sala)
    return render_template('edit_sala.html', sala=sala)

@app.route('/sala/<int:id_sala>/edit', methods=['POST'])
@login_required
def update_sala(id_sala):
    sala = Sala.query.get_or_404(id_sala)
    sala.nombre_sala = request.form['nombre_sala']
    db.session.commit()
    return redirect(url_for('salas'))

# Taller CRUD
@app.route('/talleres')
@login_required
def talleres():
    talleres = Taller.query.all()
    return render_template('talleres.html', talleres=talleres)

@app.route('/taller', methods=['POST'])
@login_required
def create_taller():
    nombre = request.form['nombre']
    horario = request.form['horario']
    id_sala = request.form['id_sala']
    id_docente = request.form['id_docente']
    
    nuevo_taller = Taller(
        nombre=nombre,
        horario=horario,
        id_sala=id_sala,
        id_docente=id_docente
    )
    
    db.session.add(nuevo_taller)
    db.session.commit()
    return redirect(url_for('talleres'))

@app.route('/taller/<int:taller_id>/delete', methods=['POST'])
@login_required
def delete_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    db.session.delete(taller)
    db.session.commit()
    return redirect(url_for('talleres'))

@app.route('/taller/<int:taller_id>/edit', methods=['GET'])
@login_required
def edit_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    docentes = DOCENTE.query.all()
    salas = Sala.query.all()
    return render_template('edit_taller.html', taller=taller, docentes=docentes, salas=salas)

@app.route('/taller/<int:taller_id>/edit', methods=['POST'])
@login_required
def update_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    taller.nombre = request.form['nombre']
    taller.horario = request.form['horario']
    taller.id_docente = request.form['id_docente']
    taller.id_sala = request.form['id_sala']
    
    db.session.commit()
    return redirect(url_for('talleres'))

@app.route('/taller/new')
@login_required
def new_taller():
    docentes = DOCENTE.query.all()
    salas = Sala.query.all()
    return render_template('create_taller.html', docentes=docentes, salas=salas)

# Clase CRUD
@app.route('/clases')
@login_required
def clases():
    clases = Clase.query.all()
    talleres = Taller.query.all()
    return render_template('clases.html', clases=clases, talleres=talleres)

@app.route('/clase', methods=['POST'])
@login_required
def create_clase():
    taller_id = request.form['taller_id']
    fecha = request.form['fecha']
    comentario_bitacora = request.form.get('comentario_bitacora')
    
    nueva_clase = Clase(
        taller_id=taller_id,
        fecha=fecha,
        comentario_bitacora=comentario_bitacora
    )
    
    db.session.add(nueva_clase)
    db.session.commit()
    return redirect(url_for('clases'))

@app.route('/clase/<int:id_clase>/delete', methods=['POST'])
@login_required
def delete_clase(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    db.session.delete(clase)
    db.session.commit()
    return redirect(url_for('clases'))

@app.route('/clase/<int:id_clase>/edit', methods=['GET'])
@login_required
def edit_clase(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    return render_template('edit_clase.html', clase=clase)

@app.route('/clase/<int:id_clase>/edit', methods=['POST'])
@login_required
def update_clase(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    clase.taller_id = request.form['taller_id']
    clase.fecha = request.form['fecha']
    clase.comentario_bitacora = request.form.get('comentario_bitacora')
    
    db.session.commit()
    return redirect(url_for('clases'))

# Estudiantes CRUD
@app.route('/estudiantes')
@login_required
def estudiantes():
    estudiantes = Estudiantes.query.all()
    return render_template('estudiantes.html', estudiantes=estudiantes)

@app.route('/estudiante', methods=['POST'])
@login_required
def create_estudiante():
    rut_estudiante = request.form['rut_estudiante']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    curso = request.form.get('curso')
    correo_institucional = request.form.get('correo_institucional')
    
    nuevo_estudiante = Estudiantes(
        rut_estudiante=rut_estudiante,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        curso=curso,
        correo_institucional=correo_institucional
    )
    
    db.session.add(nuevo_estudiante)
    db.session.commit()
    return redirect(url_for('estudiantes'))

@app.route('/estudiante/<int:id_estudiante>/delete', methods=['POST'])
@login_required
def delete_estudiante(id_estudiante):
    estudiante = Estudiantes.query.get_or_404(id_estudiante)
    db.session.delete(estudiante)
    db.session.commit()
    return redirect(url_for('estudiantes'))

@app.route('/estudiante/<int:id_estudiante>/edit', methods=['GET'])
@login_required
def edit_estudiante(id_estudiante):
    estudiante = Estudiantes.query.get_or_404(id_estudiante)
    return render_template('edit_estudiante.html', estudiante=estudiante)

@app.route('/estudiante/<int:id_estudiante>/edit', methods=['POST'])
@login_required
def update_estudiante(id_estudiante):
    estudiante = Estudiantes.query.get_or_404(id_estudiante)
    estudiante.rut_estudiante = request.form['rut_estudiante']
    estudiante.nombre = request.form['nombre']
    estudiante.apellido_paterno = request.form['apellido_paterno']
    estudiante.apellido_materno = request.form['apellido_materno']
    estudiante.curso = request.form.get('curso')
    estudiante.correo_institucional = request.form.get('correo_institucional')
    
    db.session.commit()
    return redirect(url_for('estudiantes'))

# EstudianteTaller CRUD
@app.route('/estudiantestaller', methods=['GET', 'POST'])
@login_required
def estudiante_talleres():
    if request.method == 'POST':
        taller_id = request.form['taller_id']
        if taller_id:
            estudiante_talleres = EstudianteTaller.query.filter_by(taller_id=taller_id).all()
        else:
            estudiante_talleres = EstudianteTaller.query.all()
    else:
        estudiante_talleres = EstudianteTaller.query.all()

    talleres = Taller.query.all()
    return render_template('estudiantestaller.html', estudiante_talleres=estudiante_talleres, talleres=talleres)

@app.route('/estudiantetaller', methods=['POST'])
@login_required
def create_estudiante_taller():
    taller_id = request.form['taller_id']
    id_estudiantes = request.form.getlist('id_estudiantes')
    
    for id_estudiante in id_estudiantes:
        nuevo_estudiante_taller = EstudianteTaller(
            id_estudiante=id_estudiante,
            taller_id=taller_id
        )
        db.session.add(nuevo_estudiante_taller)
    
    db.session.commit()
    return redirect(url_for('estudiante_talleres'))

@app.route('/estudiantetaller/<int:id_taller_estudiante>/delete', methods=['POST'])
@login_required
def delete_estudiante_taller(id_taller_estudiante):
    estudiante_taller = EstudianteTaller.query.get_or_404(id_taller_estudiante)
    db.session.delete(estudiante_taller)
    db.session.commit()
    return redirect(url_for('estudiante_talleres'))

@app.route('/estudiantetaller/new')
@login_required
def new_estudiante_taller():
    estudiantes = Estudiantes.query.all()
    talleres = Taller.query.all()
    cursos = db.session.query(Estudiantes.curso).distinct().all()
    cursos = [curso[0] for curso in cursos]
    return render_template('create_estudiante_taller.html', estudiantes=estudiantes, talleres=talleres, cursos=cursos)

# AsistenciaEstudiante CRUD
@app.route('/asistencia/select_clase', methods=['GET', 'POST'])
@login_required
def select_clase():
    if request.method == 'POST':
        id_clase = request.form['id_clase']
        return redirect(url_for('take_attendance', id_clase=id_clase))
    clases = Clase.query.options(db.joinedload(Clase.taller)).all()
    return render_template('select_clase.html', clases=clases)

@app.route('/asistencia/<int:id_clase>', methods=['GET', 'POST'])
@login_required
def take_attendance(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    estudiantes_taller = EstudianteTaller.query.filter_by(taller_id=clase.taller_id).all()
    estudiantes = [et.estudiante for et in estudiantes_taller]

    if request.method == 'POST':
        for estudiante in estudiantes:
            presencia = 'presencia_{}'.format(estudiante.id_estudiante) in request.form
            justificacion = request.form.get(f'justificacion_{estudiante.id_estudiante}', '')

            asistencia = AsistenciaEstudiante.query.filter_by(id_clase=id_clase, id_estudiante=estudiante.id_estudiante).first()
            if asistencia:
                asistencia.presencia = presencia
                asistencia.justificacion = justificacion
            else:
                nueva_asistencia = AsistenciaEstudiante(
                    id_clase=id_clase,
                    id_estudiante=estudiante.id_estudiante,
                    presencia=presencia,
                    justificacion=justificacion
                )
                db.session.add(nueva_asistencia)
        db.session.commit()
        return redirect(url_for('select_clase'))

    asistencias = {a.id_estudiante: a for a in AsistenciaEstudiante.query.filter_by(id_clase=id_clase).all()}
    return render_template('take_attendance.html', clase=clase, estudiantes=estudiantes, asistencias=asistencias)

@app.route('/attendance_report')
@login_required
def attendance_report():
    talleres = Taller.query.all()
    report_data = []

    for taller in talleres:
        clases = Clase.query.filter_by(taller_id=taller.taller_id).all()
        for clase in clases:
            total_estudiantes = EstudianteTaller.query.filter_by(taller_id=taller.taller_id).count()
            asistencias = AsistenciaEstudiante.query.filter_by(id_clase=clase.id_clase).all()
            presentes = sum(1 for a in asistencias if a.presencia)
            ausentes = total_estudiantes - presentes
            porcentaje_asistencia = (presentes / total_estudiantes) * 100 if total_estudiantes else 0

            report_data.append({
                'fecha': clase.fecha,
                'taller': taller.nombre,
                'taller_id': taller.taller_id,
                'clase_id': clase.id_clase,
                'total': total_estudiantes,
                'presentes': presentes,
                'ausentes': ausentes,
                'porcentaje_asistencia': porcentaje_asistencia
            })

    return render_template('attendance_report.html', report_data=report_data)

@app.route('/attendance_details/<int:id_clase>')
@login_required
def attendance_details(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    asistencias = AsistenciaEstudiante.query.filter_by(id_clase=id_clase).all()
    estudiantes_ausentes = [a.estudiante for a in asistencias if not a.presencia]
    return render_template('attendance_details.html', clase=clase, estudiantes_ausentes=estudiantes_ausentes)

# Bitacoras
@app.route('/taller_bitacoras')
@login_required
def taller_bitacoras():
    talleres = Taller.query.all()
    return render_template('taller_bitacoras.html', talleres=talleres)

@app.route('/taller_bitacoras/<int:taller_id>')
@login_required
def ver_bitacoras(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    clases = Clase.query.filter_by(taller_id=taller_id).order_by(Clase.fecha).all()
    return render_template('ver_bitacoras.html', taller=taller, clases=clases)

# Importar Excel
@app.route('/cargar_estudiantes', methods=['GET', 'POST'])
@login_required
def cargar_estudiantes():
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se ha seleccionado ningún archivo')
            return redirect(request.url)
        
        archivo = request.files['archivo']

        if archivo.filename == '':
            flash('No se ha seleccionado ningún archivo')
            return redirect(request.url)

        if archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo.save(filepath)
            cargar_datos_excel(filepath)
            flash('Los estudiantes se han cargado exitosamente')
            return redirect(url_for('estudiantes'))
    
    return render_template('cargar_estudiantes.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']

def cargar_datos_excel(filepath):
    df = pd.read_excel(filepath)
    for index, row in df.iterrows():
        nuevo_estudiante = Estudiantes(
            rut_estudiante=row['rut_estudiante'],
            nombre=row['nombre'],
            apellido_paterno=row['apellido_paterno'],
            apellido_materno=row['apellido_materno'],
            curso=row['curso'],
            correo_institucional=row['correo_institucional']
        )
        db.session.add(nuevo_estudiante)
    db.session.commit()
    os.remove(filepath)

def tablas_creadas():
    inspector = inspect(db.engine)
    return inspector.get_table_names()

if __name__ == '__main__':
    app.run(debug=True)

# Comprobar si las tablas están creadas antes de crearlas
with app.app_context():
    tablas = tablas_creadas()
    if 'nombre_tabla' not in tablas:
        db.create_all()
