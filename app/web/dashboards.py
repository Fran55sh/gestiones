from pathlib import Path
from flask import Blueprint, send_file, current_app, render_template, session

from ..utils.security import require_role

bp = Blueprint('dashboards', __name__)


@bp.route('/dashboard-admin')
@require_role('admin')
def dashboard_admin():
    return render_template('dashboard-admin.html')


@bp.route('/dashboard-gestor')
@require_role('gestor')
def dashboard_gestor():
    # Pasar user_id al template para que el JavaScript pueda usarlo
    user_id = session.get('user_id')
    return render_template('dashboard-gestor.html', user_id=user_id)


@bp.route('/dashboard-user')
@require_role('user')
def dashboard_user():
    return render_template('dashboard-user.html')
