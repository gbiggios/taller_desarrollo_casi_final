from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from datetime import datetime, timedelta
from ..models import Clase, Taller
from ..extensions import db

clases_bp = Blueprint('clases', __name__)

@clases_bp.route('/')
@login_required
def clases():
    clases = Clase.query.all()
    talleres = Taller.query.all()
    return render_template('clases.html', clases=clases, talleres=talleres)

@clases_bp.route('/create', methods=['POST'])
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
    return redirect(url_for('clases.clases'))

@clases_bp.route('/multiple', methods=['POST'])
@login_required
def create_multiple_clases():
    taller_id = request.form['taller_id']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    dia_semana = request.form['dia_semana']
    comentario_bitacora = request.form.get('comentario_bitacora')

    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    dias_semana = {
        'Lunes': 0,
        'Martes': 1,
        'Miércoles': 2,
        'Jueves': 3,
        'Viernes': 4,
    }

    dia_semana_num = dias_semana[dia_semana]

    while fecha_inicio <= fecha_fin:
        if fecha_inicio.weekday() == dia_semana_num:
            nueva_clase = Clase(
                taller_id=taller_id,
                fecha=fecha_inicio,
                comentario_bitacora=comentario_bitacora
            )
            db.session.add(nueva_clase)
        fecha_inicio += timedelta(days=1)

    db.session.commit()
    return redirect(url_for('clases.clases'))

@clases_bp.route('/<int:id_clase>/delete', methods=['POST'])
@login_required
def delete_clase(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    db.session.delete(clase)
    db.session.commit()
    return redirect(url_for('clases.clases'))

@clases_bp.route('/<int:id_clase>/edit', methods=['GET', 'POST'])
@login_required
def edit_clase(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    if request.method == 'POST':
        clase.comentario_bitacora = request.form['comentario_bitacora']
        db.session.commit()
        return redirect(url_for('clases.clases'))
    return render_template('edit_clase.html', clase=clase)
