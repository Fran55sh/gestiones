"""
Endpoints API para datos del dashboard y casos.
"""

from datetime import datetime
from flask import request, jsonify, session
from flask import current_app as app
from sqlalchemy import or_

from ...core.database import db
from ...features.cases.models import Case
from ...features.cases.promise import Promise
from ...features.activities.models import Activity
from ...services.dashboard import (
    get_kpis,
    get_performance_chart_data,
    get_cartera_distribution,
    get_gestores_ranking,
    get_cases_status_distribution,
    get_comparison_data,
)
from ...utils.security import require_role
from ...utils.exceptions import ValidationError
from ...services.audit import audit_log
from ...services.cache import invalidate_cache

# Use the parent blueprint from __init__.py
from . import bp


def _parse_date(date_str: str) -> datetime:
    """Parsea una fecha desde string ISO."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError(f"Fecha inválida: {date_str}", field="date")


@bp.route("/dashboard/kpis")
@require_role("admin")
def dashboard_kpis():
    """Obtiene KPIs del dashboard."""
    try:
        start_date = _parse_date(request.args.get("start_date"))
        end_date = _parse_date(request.args.get("end_date"))
        cartera = request.args.get("cartera")
        gestor_id = request.args.get("gestor_id", type=int)

        kpis = get_kpis(start_date, end_date, cartera, gestor_id)
        return jsonify({"success": True, "data": kpis})
    except Exception as e:
        app.logger.error(f"Error obteniendo KPIs: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/dashboard/charts/performance")
@require_role("admin")
def dashboard_performance_chart():
    """Obtiene datos para gráfico de rendimiento."""
    try:
        start_date = _parse_date(request.args.get("start_date"))
        end_date = _parse_date(request.args.get("end_date"))
        cartera = request.args.get("cartera")

        data = get_performance_chart_data(start_date, end_date, cartera)
        return jsonify({"success": True, "data": data})
    except Exception as e:
        app.logger.error(f"Error obteniendo datos de rendimiento: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/dashboard/charts/cartera")
@require_role("admin")
def dashboard_cartera_chart():
    """Obtiene distribución por cartera."""
    try:
        data = get_cartera_distribution()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        app.logger.error(f"Error obteniendo distribución de cartera: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/dashboard/gestores/ranking")
@require_role("admin")
def dashboard_gestores_ranking():
    """Obtiene ranking de gestores."""
    try:
        limit = request.args.get("limit", 10, type=int)
        ranking = get_gestores_ranking(limit)
        return jsonify({"success": True, "data": ranking})
    except Exception as e:
        app.logger.error(f"Error obteniendo ranking: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/dashboard/stats/comparison")
@require_role("admin")
def dashboard_comparison():
    """Obtiene comparativa temporal."""
    try:
        data = get_comparison_data()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        app.logger.error(f"Error obteniendo comparativa: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/dashboard/cases/status")
@require_role("admin")
def dashboard_cases_status():
    """Obtiene distribución de casos por estado."""
    try:
        data = get_cases_status_distribution()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        app.logger.error(f"Error obteniendo distribución de estados: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases")
@require_role("admin")
def list_cases():
    """Lista casos con filtros y paginación."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        status = request.args.get("status")
        cartera = request.args.get("cartera")
        gestor_id = request.args.get("gestor_id", type=int)
        search = request.args.get("search")

        query = Case.query

        # Aplicar filtros
        if status:
            query = query.filter(Case.status == status)
        if cartera:
            query = query.filter(Case.cartera == cartera)
        if gestor_id:
            query = query.filter(Case.assigned_to_id == gestor_id)
        if search:
            query = query.filter(
                or_(Case.debtor_name.ilike(f"%{search}%"), Case.dni.ilike(f"%{search}%"), Case.entity.ilike(f"%{search}%"))
            )

        # Paginación
        pagination = query.order_by(Case.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify(
            {
                "success": True,
                "data": [c.to_dict() for c in pagination.items],
                "pagination": {"page": page, "per_page": per_page, "total": pagination.total, "pages": pagination.pages},
            }
        )
    except Exception as e:
        app.logger.error(f"Error listando casos: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases", methods=["POST"])
@require_role("admin")
def create_case():
    """Crea un nuevo caso."""
    try:
        data = request.get_json()

        # Validar campos requeridos
        required_fields = ["entity", "debtor_name", "amount", "cartera"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Campo requerido: {field}", field=field)

        case = Case(
            entity=data["entity"],
            debtor_name=data["debtor_name"],
            dni=data.get("dni"),
            amount=data["amount"],
            status=data.get("status", "en_gestion"),
            management_status=data.get("management_status", "sin-gestion"),
            cartera=data["cartera"],
            assigned_to_id=data.get("assigned_to_id"),
            notes=data.get("notes"),
        )

        db.session.add(case)
        db.session.commit()

        # Invalidar cache relacionado
        invalidate_cache("cache:dashboard:*")
        invalidate_cache("cache:kpis:*")

        audit_log("create_case", {"case_id": case.id, "entity": case.entity, "amount": float(case.amount)})

        return jsonify({"success": True, "data": case.to_dict()}), 201
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creando caso: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases/<int:case_id>")
def get_case(case_id):
    """Obtiene un caso por ID. Admin puede ver todos, gestor solo sus casos asignados."""
    from werkzeug.exceptions import NotFound

    try:
        user_role = session.get("role")
        user_id = session.get("user_id")

        if not user_role or not user_id:
            return jsonify({"success": False, "error": "No autorizado"}), 401

        case = Case.query.get_or_404(case_id)

        # Si es gestor, solo puede ver sus casos asignados
        if user_role == "gestor" and case.assigned_to_id != user_id:
            app.logger.warning(f"Gestor {user_id} intentó acceder al caso {case_id} que no le pertenece")
            return jsonify({"success": False, "error": "No tiene permisos para ver este caso"}), 403

        return jsonify({"success": True, "data": case.to_dict(include_relations=True)})
    except NotFound:
        # Propagar el 404 sin convertirlo en 500
        return jsonify({"success": False, "error": "Caso no encontrado"}), 404
    except Exception as e:
        app.logger.error(f"Error obteniendo caso: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases/<int:case_id>", methods=["PUT"])
@require_role("admin")
def update_case(case_id):
    """Actualiza un caso."""
    try:
        case = Case.query.get_or_404(case_id)
        data = request.get_json()

        # Actualizar campos permitidos
        if "entity" in data:
            case.entity = data["entity"]
        if "debtor_name" in data:
            case.debtor_name = data["debtor_name"]
        if "dni" in data:
            case.dni = data["dni"]
        if "amount" in data:
            case.amount = data["amount"]
        if "status" in data:
            case.status = data["status"]
        if "cartera" in data:
            case.cartera = data["cartera"]
        if "assigned_to_id" in data:
            case.assigned_to_id = data["assigned_to_id"]
        if "notes" in data:
            case.notes = data["notes"]

        db.session.commit()

        # Invalidar cache relacionado
        invalidate_cache("cache:dashboard:*")
        invalidate_cache("cache:kpis:*")

        audit_log("update_case", {"case_id": case_id, "changes": data})

        return jsonify({"success": True, "data": case.to_dict()})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error actualizando caso: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases/<int:case_id>", methods=["DELETE"])
@require_role("admin")
def delete_case(case_id):
    """Elimina un caso."""
    try:
        case = Case.query.get_or_404(case_id)
        case_data = case.to_dict()
        db.session.delete(case)
        db.session.commit()

        audit_log("delete_case", {"case_id": case_id, "case_data": case_data})

        return jsonify({"success": True, "message": "Caso eliminado exitosamente"})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error eliminando caso: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases/<int:case_id>/promises", methods=["POST"])
@require_role("admin")
def create_promise(case_id):
    """Crea una promesa de pago para un caso."""
    try:
        case = Case.query.get_or_404(case_id)  # noqa: F841
        data = request.get_json()

        if "amount" not in data or "promise_date" not in data:
            raise ValidationError("amount y promise_date son requeridos")

        from datetime import datetime as dt

        promise_date = dt.fromisoformat(data["promise_date"].replace("Z", "+00:00")).date()

        promise = Promise(
            case_id=case_id,
            amount=data["amount"],
            promise_date=promise_date,
            status=data.get("status", "pending"),
            notes=data.get("notes"),
        )

        db.session.add(promise)
        db.session.commit()

        return jsonify({"success": True, "data": promise.to_dict()}), 201
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creando promesa: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases/<int:case_id>/activities", methods=["POST"])
@require_role("admin")
def create_activity(case_id):
    """Crea una actividad para un caso."""
    try:
        case = Case.query.get_or_404(case_id)  # noqa: F841
        data = request.get_json()

        if "type" not in data:
            raise ValidationError("type es requerido")

        user_id = session.get("user_id")
        if not user_id:
            raise ValidationError("Usuario no autenticado")

        activity = Activity(case_id=case_id, type=data["type"], notes=data.get("notes"), created_by_id=user_id)

        db.session.add(activity)
        db.session.commit()

        return jsonify({"success": True, "data": activity.to_dict()}), 201
    except ValidationError:
        raise
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creando actividad: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/update-status", methods=["POST"])
def update_status():
    """
    Endpoint para actualizar el estado de un caso desde el dashboard de gestor.
    Compatible con HTMX. Acepta gestor o admin.
    """
    try:
        # Verificar autenticación
        user_role = session.get("role")
        if user_role not in ["admin", "gestor"]:
            return jsonify({"success": False, "error": "No autorizado"}), 401

        # Obtener datos del formulario (HTMX envía form-data)
        case_id = request.form.get("case_id", type=int)
        # HTMX envía el valor del select con el name del select
        status = request.form.get("status-selector") or request.form.get("status") or request.form.get("value")

        app.logger.info(f"Update status request - case_id: {case_id}, status: {status}, form data: {dict(request.form)}")

        if not status:
            return jsonify({"success": False, "error": "status es requerido"}), 400

        if not case_id:
            app.logger.warning(
                f"Update status sin case_id - solo actualización UI. Status: {status}, Form data: {dict(request.form)}"
            )

        # Si no hay case_id, es solo una actualización de UI (no hay caso específico)
        # Esto puede pasar si el usuario cambia el estado antes de cargar un cliente
        # Retornar respuesta HTML para actualizar el badge pero sin guardar
        if not case_id:
            status_badges = {
                "sin-gestion": '<span class="status-badge status-sin-gestion">Sin Gestión</span>',
                "contactado": '<span class="status-badge status-contactado">Contactado</span>',
                "con-arreglo": '<span class="status-badge status-con-arreglo">Con Arreglo</span>',
                "incobrable": '<span class="status-badge status-incobrable">Incobrable</span>',
                "de-baja": '<span class="status-badge status-de-baja">De Baja</span>',
            }
            badge_html = status_badges.get(status, f'<span class="status-badge">{status}</span>')

            # Respuesta HTML para HTMX (solo actualiza el badge visual)
            if request.headers.get("HX-Request"):
                return (
                    f"""
                <div id="management-status-card" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-gray-800">Estado de Gestión</h3>
                    </div>
                    <div id="current-status-display">
                        {badge_html}
                    </div>
                </div>
                """,
                    200,
                )

            return jsonify({"success": True, "message": "Estado actualizado (solo UI)"})

        # Si hay case_id, actualizar el caso en la BD
        case = Case.query.get_or_404(case_id)
        user_id = session.get("user_id")

        # Solo el gestor asignado o admin puede actualizar
        if user_role != "admin" and case.assigned_to_id != user_id:
            return jsonify({"success": False, "error": "No tiene permisos para actualizar este caso"}), 403

        # Mapear estados del frontend a estados de la BD
        status_map = {
            "sin-gestion": "en_gestion",
            "contactado": "en_gestion",
            "con-arreglo": "promesa",
            "incobrable": "incobrable",
            "de-baja": "incobrable",
            "pagada": "pagada",
        }

        old_status = case.status
        old_management_status = case.management_status
        new_status = status_map.get(status, status)

        # Actualizar tanto status como management_status
        case.status = new_status
        case.management_status = status  # Guardar el estado detallado del frontend
        db.session.commit()

        # Invalidar cache
        invalidate_cache("cache:dashboard:*")
        invalidate_cache("cache:kpis:*")

        audit_log(
            "update_case_status",
            {
                "case_id": case_id,
                "old_status": old_status,
                "old_management_status": old_management_status,
                "new_status": new_status,
                "new_management_status": status,
            },
        )

        app.logger.info(
            f"Estado actualizado: Caso {case_id} de '{old_status}'/'{old_management_status}' a '{new_status}'/'{status}'"
        )

        # Recargar el caso para obtener datos actualizados
        db.session.refresh(case)

        # Respuesta para HTMX (HTML) - Incluir el selector actualizado también
        if request.headers.get("HX-Request"):
            status_badges = {
                "sin-gestion": '<span class="status-badge status-sin-gestion">Sin Gestión</span>',
                "contactado": '<span class="status-badge status-contactado">Contactado</span>',
                "con-arreglo": '<span class="status-badge status-con-arreglo">Con Arreglo</span>',
                "incobrable": '<span class="status-badge status-incobrable">Incobrable</span>',
                "de-baja": '<span class="status-badge status-de-baja">De Baja</span>',
            }
            badge_html = status_badges.get(status, f'<span class="status-badge">{status}</span>')

            # Usar management_status si está disponible, sino mapear desde status
            if case.management_status:
                frontend_status = case.management_status
            else:
                # Mapeo de respaldo si no hay management_status
                status_to_frontend = {
                    "en_gestion": "contactado",
                    "promesa": "con-arreglo",
                    "pagada": "pagada",
                    "incobrable": "incobrable",
                }
                frontend_status = status_to_frontend.get(case.status, status)

            return (
                f"""
            <div id="management-status-card" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-800">Estado de Gestión</h3>
                </div>
                <div class="space-y-4">
                    <label class="block text-sm font-medium text-gray-700 mb-3">Seleccionar Estado</label>
                    <input type="hidden" id="current-case-id" name="case_id" value="{case.id}">
                    <select
                        id="status-selector"
                        name="status-selector"
                        class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all text-base font-semibold"
                        onchange="updateStatusBadge(this.value)"
                        hx-post="/api/update-status"
                        hx-target="#management-status-card"
                        hx-swap="outerHTML"
                        hx-trigger="change"
                        hx-include="#current-case-id"
                        hx-indicator="#status-loading">
                        <option value="sin-gestion" {'selected' if frontend_status == 'sin-gestion' else ''}>Sin Gestión</option>
                        <option value="contactado" {'selected' if frontend_status == 'contactado' else ''}>Contactado</option>
                        <option value="con-arreglo" {'selected' if frontend_status == 'con-arreglo' else ''}>Con Arreglo</option>
                        <option value="incobrable" {'selected' if frontend_status == 'incobrable' else ''}>Incobrable</option>
                        <option value="de-baja" {'selected' if frontend_status == 'de-baja' else ''}>De Baja</option>
                    </select>
                    <div class="flex items-center gap-2 text-sm text-gray-500" id="status-loading" style="display: none;">
                        <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i>
                        Guardando estado...
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-200">
                        <p class="text-sm text-gray-600 mb-2">Estado Actual:</p>
                        <div id="current-status-display">
                            {badge_html}
                        </div>
                    </div>
                </div>
            </div>
            """,
                200,
            )

        # Respuesta JSON para peticiones normales
        return jsonify({"success": True, "data": case.to_dict()})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error actualizando estado: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases/gestor")
def get_gestor_cases():
    """Obtiene casos del gestor actual."""
    try:
        user_id = session.get("user_id")
        user_role = session.get("role")

        if not user_id:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401

        # Si es admin, puede ver todos los casos
        # Si es gestor, solo sus casos
        query = Case.query
        if user_role == "gestor":
            query = query.filter(Case.assigned_to_id == user_id)

        # Filtros opcionales
        cartera = request.args.get("cartera")
        if cartera:
            query = query.filter(Case.cartera == cartera)

        status = request.args.get("status")
        if status:
            query = query.filter(Case.status == status)

        # Ordenar por fecha de creación
        cases = query.order_by(Case.created_at.desc()).all()

        return jsonify({"success": True, "data": [c.to_dict(include_relations=True) for c in cases]})
    except Exception as e:
        app.logger.error(f"Error obteniendo casos del gestor: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/register-management", methods=["POST"])
def register_management():
    """
    Endpoint para registrar una gestión desde el dashboard de gestor.
    Compatible con HTMX.
    """
    try:
        # Verificar autenticación
        user_role = session.get("role")
        if user_role not in ["admin", "gestor"]:
            return jsonify({"success": False, "error": "No autorizado"}), 401

        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401

        # Obtener datos del formulario
        case_id = request.form.get("case_id", type=int)
        activity_type = request.form.get("type", "note")
        notes = request.form.get("notes", "")

        if not case_id:
            return jsonify({"success": False, "error": "case_id es requerido"}), 400

        # Validar que el caso existe
        case = Case.query.get_or_404(case_id)

        # Solo el gestor asignado o admin puede registrar gestiones
        if user_role != "admin" and case.assigned_to_id != user_id:
            return jsonify({"success": False, "error": "No tiene permisos para este caso"}), 403

        # Crear actividad
        activity = Activity(case_id=case_id, type=activity_type, notes=notes, created_by_id=user_id)

        db.session.add(activity)
        db.session.commit()

        audit_log("register_management", {"case_id": case_id, "activity_type": activity_type})

        # Recargar para obtener relaciones
        db.session.refresh(activity)

        # Respuesta para HTMX - renderizar la gestión como HTML
        if request.headers.get("HX-Request"):
            created_at = activity.created_at.strftime("%d/%m/%Y - %H:%M") if activity.created_at else "Ahora"
            creator_name = activity.creator.username if activity.creator else "Usuario"

            return (
                f"""
            <div class="border-l-4 border-green-500 pl-4 pb-4" id="activity-{activity.id}">
                <div class="flex items-start justify-between mb-2">
                    <div class="flex items-center gap-2">
                        <i data-lucide="user" class="w-4 h-4 text-gray-400"></i>
                        <span class="text-sm font-semibold text-gray-900">{creator_name}</span>
                        <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Nueva</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-500">{created_at}</span>
                        <button
                            onclick="deleteActivity({activity.id})"
                            class="text-red-500 hover:text-red-700 transition-colors"
                            title="Eliminar gestión">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
                <p class="text-sm text-gray-700 leading-relaxed">{activity.notes}</p>
            </div>
            <script>
                if (typeof lucide !== 'undefined' && lucide.createIcons) {{
                    lucide.createIcons();
                }}
            </script>
            """,
                200,
            )

        return jsonify({"success": True, "data": activity.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error registrando gestión: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
