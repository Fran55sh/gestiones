"""
Endpoints API para gestiones/actividades.
"""
from flask import Blueprint, request, jsonify, session
from ...core.database import db
from ...features.activities.models import Activity
from ...features.cases.models import Case
from ...services.audit import audit_log
import logging

# Use the parent blueprint from __init__.py
from . import bp
logger = logging.getLogger(__name__)


@bp.route('/<int:activity_id>', methods=['DELETE'])
def delete_activity(activity_id):
    """Elimina una actividad/gestión."""
    try:
        user_role = session.get('role')
        user_id = session.get('user_id')
        
        if not user_role or not user_id:
            return jsonify({
                'success': False,
                'error': 'No autorizado'
            }), 401
        
        activity = Activity.query.get_or_404(activity_id)
        
        # Solo el creador o admin pueden eliminar
        if user_role != 'admin' and activity.created_by_id != user_id:
            logger.warning(f"Usuario {user_id} intentó eliminar actividad {activity_id} que no creó")
            return jsonify({
                'success': False,
                'error': 'No tiene permisos para eliminar esta gestión'
            }), 403
        
        case_id = activity.case_id
        
        # Eliminar
        db.session.delete(activity)
        db.session.commit()
        
        audit_log('delete_activity', {
            'activity_id': activity_id,
            'case_id': case_id
        })
        
        logger.info(f"Actividad {activity_id} eliminada por usuario {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Gestión eliminada correctamente'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando actividad: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/case/<int:case_id>', methods=['GET'])
def get_case_activities(case_id):
    """Obtiene todas las actividades de un caso."""
    try:
        user_role = session.get('role')
        user_id = session.get('user_id')
        
        if not user_role or not user_id:
            return jsonify({
                'success': False,
                'error': 'No autorizado'
            }), 401
        
        # Verificar que el usuario tiene acceso al caso
        case = Case.query.get_or_404(case_id)
        
        if user_role == 'gestor' and case.assigned_to_id != user_id:
            return jsonify({
                'success': False,
                'error': 'No tiene permisos para ver las gestiones de este caso'
            }), 403
        
        # Obtener actividades ordenadas por fecha (más recientes primero)
        activities = Activity.query.filter_by(case_id=case_id).order_by(
            Activity.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [activity.to_dict() for activity in activities]
        })
    except Exception as e:
        logger.error(f"Error obteniendo actividades del caso {case_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

