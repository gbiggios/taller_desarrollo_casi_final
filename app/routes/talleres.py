from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from ..models import Taller, Sala, DOCENTE
from ..extensions import db

talleres_bp = Blueprint('talleres', __name__)

@talleres_bp.route('/')
@login_required
def talleres():
    talleres = Taller.query.all()
    salas = Sala.query.all()
    docentes = DOCENTE.query.all()
    return render_template('talleres.html', talleres=talleres, salas=salas, docentes=docentes)

@talleres_bp.route('/create', methods=['POST'])
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
    return redirect(url_for('talleres.talleres'))

@talleres_bp.route('/<int:taller_id>/delete', methods=['POST'])
@login_required
def delete_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    db.session.delete(taller)
    db.session.commit()
    return redirect(url_for('talleres.talleres'))

@talleres_bp.route('/<int:taller_id>/edit', methods=['GET'])
@login_required
def edit_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    salas = Sala.query.all()
    docentes = DOCENTE.query.all()
    return render_template('edit_taller.html', taller=taller, salas=salas, docentes=docentes)

@talleres_bp.route('/<int:taller_id>/edit', methods=['POST'])
@login_required
def update_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    taller.nombre = request.form['nombre']
    taller.horario = request.form['horario']
    taller.id_sala = request.form['id_sala']
    taller.id_docente = request.form['id_docente']
    
    db.session.commit()
    return redirect(url_for('talleres.talleres'))
