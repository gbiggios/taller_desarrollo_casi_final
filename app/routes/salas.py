# app/routes/salas.py
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from ..models import Sala
from ..extensions import db

salas_bp = Blueprint('salas', __name__)

@salas_bp.route('/')
@login_required
def salas():
    salas = Sala.query.all()
    return render_template('salas.html', salas=salas)

@salas_bp.route('/sala', methods=['POST'])
@login_required
def create_sala():
    nombre_sala = request.form['nombre_sala']
    nueva_sala = Sala(nombre_sala=nombre_sala)
    db.session.add(nueva_sala)
    db.session.commit()
    return redirect(url_for('salas.salas'))

@salas_bp.route('/sala/<int:id_sala>/delete', methods=['POST'])
@login_required
def delete_sala(id_sala):
    sala = Sala.query.get_or_404(id_sala)
    db.session.delete(sala)
    db.session.commit()
    return redirect(url_for('salas.salas'))

@salas_bp.route('/sala/<int:id_sala>/edit', methods=['GET'])
@login_required
def edit_sala(id_sala):
    sala = Sala.query.get_or_404(id_sala)
    return render_template('edit_sala.html', sala=sala)

@salas_bp.route('/sala/<int:id_sala>/edit', methods=['POST'])
@login_required
def update_sala(id_sala):
    sala = Sala.query.get_or_404(id_sala)
    sala.nombre_sala = request.form['nombre_sala']
    db.session.commit()
    return redirect(url_for('salas.salas'))
