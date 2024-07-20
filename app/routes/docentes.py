from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from werkzeug.security import generate_password_hash
from app.models import DOCENTE, User
from app.extensions import db

docentes_bp = Blueprint('docentes', __name__)

@docentes_bp.route('/')
@login_required
def docentes():
    docentes = DOCENTE.query.all()
    return render_template('docentes.html', docentes=docentes)

@docentes_bp.route('/create', methods=['POST'])
@login_required
def create_docente():
    rut_docente = request.form['rut_docente']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    telefono = request.form['telefono']
    correo = request.form['correo']

    # Verificar si el RUT ya existe
    existing_docente = DOCENTE.query.filter_by(rut_docente=rut_docente).first()
    if existing_docente:
        flash('El RUT ya está registrado. Por favor, ingrese un RUT diferente.', 'danger')
        return redirect(url_for('docentes.docentes'))

    # Encriptar la contraseña (usar el RUT como contraseña por defecto)
    contraseña_encriptada = generate_password_hash(rut_docente, method='sha256')

    # Crear el nuevo docente
    nuevo_docente = DOCENTE(
        rut_docente=rut_docente,
        nombre=nombre,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        telefono=telefono,
        correo=correo,
        contraseña=contraseña_encriptada
    )

    db.session.add(nuevo_docente)
    db.session.commit()

    # Crear el usuario correspondiente
    nuevo_usuario = User(
        username=rut_docente,
        password=contraseña_encriptada,
        id_docente=nuevo_docente.id_docente
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    flash('Docente y usuario agregados exitosamente.', 'success')
    return redirect(url_for('docentes.docentes'))

@docentes_bp.route('/delete/<int:id_docente>', methods=['POST'])
@login_required
def delete_docente(id_docente):
    docente = DOCENTE.query.get_or_404(id_docente)
    db.session.delete(docente)
    db.session.commit()
    flash('Docente eliminado exitosamente.', 'success')
    return redirect(url_for('docentes.docentes'))

@docentes_bp.route('/edit/<int:id_docente>', methods=['GET', 'POST'])
@login_required
def edit_docente(id_docente):
    docente = DOCENTE.query.get_or_404(id_docente)
    if request.method == 'POST':
        docente.rut_docente = request.form['rut_docente']
        docente.nombre = request.form['nombre']
        docente.apellido_paterno = request.form['apellido_paterno']
        docente.apellido_materno = request.form['apellido_materno']
        docente.telefono = request.form['telefono']
        docente.correo = request.form['correo']
        docente.contraseña = generate_password_hash(request.form['rut_docente'], method='sha256')
        db.session.commit()
        flash('Docente actualizado exitosamente.', 'success')
        return redirect(url_for('docentes.docentes'))
    return render_template('edit_docente.html', docente=docente)
