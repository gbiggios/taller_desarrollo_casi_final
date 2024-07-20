from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
import pandas as pd
from ..models import Estudiantes
from ..extensions import db
from ..utils import allowed_file, cargar_datos_excel

estudiantes_bp = Blueprint('estudiantes', __name__)

@estudiantes_bp.route('/')
@login_required
def estudiantes():
    estudiantes = Estudiantes.query.all()
    return render_template('estudiantes.html', estudiantes=estudiantes)

@estudiantes_bp.route('/create', methods=['POST'])
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
    return redirect(url_for('estudiantes.estudiantes'))

@estudiantes_bp.route('/<int:id_estudiante>/delete', methods=['POST'])
@login_required
def delete_estudiante(id_estudiante):
    estudiante = Estudiantes.query.get_or_404(id_estudiante)
    db.session.delete(estudiante)
    db.session.commit()
    return redirect(url_for('estudiantes.estudiantes'))

@estudiantes_bp.route('/<int:id_estudiante>/edit', methods=['GET'])
@login_required
def edit_estudiante(id_estudiante):
    estudiante = Estudiantes.query.get_or_404(id_estudiante)
    return render_template('edit_estudiante.html', estudiante=estudiante)

@estudiantes_bp.route('/<int:id_estudiante>/edit', methods=['POST'])
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
    return redirect(url_for('estudiantes.estudiantes'))

@estudiantes_bp.route('/cargar_estudiantes', methods=['GET', 'POST'])
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
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            archivo.save(filepath)
            cargar_datos_excel(filepath)
            flash('Los estudiantes se han cargado exitosamente')
            return redirect(url_for('estudiantes.estudiantes'))
    
    return render_template('cargar_estudiantes.html')
