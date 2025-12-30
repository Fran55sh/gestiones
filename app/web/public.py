from pathlib import Path
from flask import Blueprint, send_file, send_from_directory, abort, current_app, request, render_template

bp = Blueprint('root', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/gestiones')
def gestiones():
    return render_template('login.html')


@bp.route('/logo.png')
@bp.route('/logo-dark.png')
def serve_logo():
    root = Path(current_app.config['ROOT_DIR'])
    return send_from_directory(str(root), request.path[1:])


@bp.route('/<path:filename>')
def serve_static_root(filename):
    """
    Sirve archivos estáticos en la raíz (no dentro de /static).
    Flask ya sirve /static automáticamente.
    """
    if 'static' in filename.split('/'):
        abort(404)
    root = Path(current_app.config['ROOT_DIR'])
    extension = Path(filename).suffix.lower()
    if extension not in current_app.config['ALLOWED_STATIC_EXTENSIONS']:
        abort(404)
    try:
        return send_from_directory(str(root), filename)
    except Exception:
        abort(404)

