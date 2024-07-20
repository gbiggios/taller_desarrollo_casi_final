from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..models import DOCENTE, Taller, Clase, AsistenciaEstudiante
from ..extensions import db

docente_bp = Blueprint('docente', __name__)

@docente_bp.route('/dashboard')
@login_required
def dashboard():
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()
    return render_template('docente_dashboard.html', talleres=talleres)

@docente_bp.route('/clase/<int:clase_id>', methods=['GET', 'POST'])
@login_required
def clase_detalle(clase_id):
    clase = Clase.query.get_or_404(clase_id)
    if request.method == 'POST':
        for estudiante in clase.taller.estudiantes_taller:
            presencia = request.form.get(f'presencia_{estudiante.id_estudiante}') == 'on'
            justificacion = request.form.get(f'justificacion_{estudiante.id_estudiante}')
            asistencia = AsistenciaEstudiante.query.filter_by(id_clase=clase.id_clase, id_estudiante=estudiante.id_estudiante).first()
            if asistencia:
                asistencia.presencia = presencia
                asistencia.justificacion = justificacion
            else:
                nueva_asistencia = AsistenciaEstudiante(
                    id_clase=clase.id_clase,
                    id_estudiante=estudiante.id_estudiante,
                    presencia=presencia,
                    justificacion=justificacion
                )
                db.session.add(nueva_asistencia)
        
        clase.comentario_bitacora = request.form['comentario_bitacora']
        db.session.commit()
        flash('Asistencia y bitácora actualizadas correctamente.')
        return redirect(url_for('docente.dashboard'))
    
    asistencias = {a.id_estudiante: a for a in AsistenciaEstudiante.query.filter_by(id_clase=clase.id_clase).all()}
    return render_template('clase_detalle.html', clase=clase, asistencias=asistencias)
