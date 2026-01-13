"""
Endpoints API para datos del dashboard y casos.
"""

from datetime import datetime
from flask import request, jsonify, session
from flask import current_app as app
from sqlalchemy import or_

from ...core.database import db
from ...features.cases.models import Case, CaseStatus
from ...features.cases.promise import Promise
from ...features.activities.models import Activity
from ...features.carteras.models import Cartera
from ...services.dashboard import (
    get_kpis,
    get_performance_chart_data,
    get_cartera_distribution,
    get_gestores_ranking,
    get_cases_status_distribution,
    get_comparison_data,
    get_clientes_con_multiples_deudas,
    get_casos_agrupados_por_dni,
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
        cartera_id = request.args.get("cartera_id", type=int)
        gestor_id = request.args.get("gestor_id", type=int)

        kpis = get_kpis(start_date, end_date, cartera_id, gestor_id)
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
        cartera_id = request.args.get("cartera_id", type=int)

        data = get_performance_chart_data(start_date, end_date, cartera_id)
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


@bp.route("/case-statuses")
def get_case_statuses():
    """Obtiene todos los estados de casos activos."""
    try:
        statuses = CaseStatus.query.filter_by(activo=True).order_by(CaseStatus.nombre).all()
        return jsonify([s.to_dict() for s in statuses])
    except Exception as e:
        app.logger.error(f"Error obteniendo estados de casos: {e}", exc_info=True)
        return jsonify({"error": "Error obteniendo estados de casos"}), 500


@bp.route("/carteras")
def get_carteras():
    """Obtiene todas las carteras (activas e inactivas para admin)."""
    try:
        # Si es admin, mostrar todas las carteras; si no, solo activas
        user_role = session.get("role")
        if user_role == "admin":
            carteras = Cartera.query.order_by(Cartera.nombre).all()
        else:
            carteras = Cartera.query.filter_by(activo=True).order_by(Cartera.nombre).all()
        return jsonify([c.to_dict() for c in carteras])
    except Exception as e:
        app.logger.error(f"Error obteniendo carteras: {e}", exc_info=True)
        return jsonify({"error": "Error obteniendo carteras"}), 500


@bp.route("/carteras", methods=["POST"])
@require_role("admin")
def create_cartera():
    """Crea una nueva cartera."""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data or "nombre" not in data or not data["nombre"].strip():
            raise ValidationError("El nombre de la cartera es requerido", field="nombre")
        
        nombre = data["nombre"].strip()
        
        # Validar que el nombre sea único
        existing = Cartera.query.filter_by(nombre=nombre).first()
        if existing:
            raise ValidationError("Ya existe una cartera con ese nombre", field="nombre")
        
        # Crear nueva cartera
        cartera = Cartera(
            nombre=nombre,
            activo=data.get("activo", True)
        )
        db.session.add(cartera)
        db.session.commit()
        
        audit_log("cartera_created", {"cartera_id": cartera.id, "nombre": cartera.nombre})
        invalidate_cache("cartera")
        
        return jsonify({"success": True, "data": cartera.to_dict()}), 201
    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creando cartera: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Error creando cartera"}), 500


@bp.route("/carteras/<int:cartera_id>", methods=["DELETE"])
@require_role("admin")
def delete_cartera(cartera_id):
    """Elimina o desactiva una cartera."""
    try:
        cartera = Cartera.query.get_or_404(cartera_id)
        
        # Verificar si tiene casos asignados
        casos_count = Case.query.filter_by(cartera_id=cartera_id).count()
        
        if casos_count > 0:
            # No eliminar físicamente, solo desactivar
            cartera.activo = False
            db.session.commit()
            audit_log("cartera_deactivated", {"cartera_id": cartera_id, "nombre": cartera.nombre, "casos_count": casos_count})
            invalidate_cache("cartera")
            return jsonify({
                "success": True,
                "message": f"Cartera desactivada (tiene {casos_count} casos asignados)",
                "data": cartera.to_dict()
            })
        else:
            # Eliminar físicamente si no tiene casos
            nombre = cartera.nombre
            db.session.delete(cartera)
            db.session.commit()
            audit_log("cartera_deleted", {"cartera_id": cartera_id, "nombre": nombre})
            invalidate_cache("cartera")
            return jsonify({"success": True, "message": "Cartera eliminada correctamente"})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error eliminando cartera: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Error eliminando cartera"}), 500


@bp.route("/cases")
@require_role("admin")
def list_cases():
    """Lista casos con filtros y paginación."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        status = request.args.get("status")
        cartera_id = request.args.get("cartera_id", type=int)
        gestor_id = request.args.get("gestor_id", type=int)
        search = request.args.get("search")

        query = Case.query

        # Aplicar filtros
        if status:
            # status puede ser un ID o un nombre de estado
            try:
                status_id = int(status)
                query = query.filter(Case.status_id == status_id)
            except ValueError:
                # Es un nombre, buscar por nombre
                status_obj = CaseStatus.query.filter_by(nombre=status, activo=True).first()
                if status_obj:
                    query = query.filter(Case.status_id == status_obj.id)
        if cartera_id:
            query = query.filter(Case.cartera_id == cartera_id)
        if gestor_id:
            query = query.filter(Case.assigned_to_id == gestor_id)
        if search:
            query = query.filter(
                or_(
                    Case.name.ilike(f"%{search}%"),
                    Case.lastname.ilike(f"%{search}%"),
                    Case.dni.ilike(f"%{search}%"),
                    Case.nro_cliente.ilike(f"%{search}%")
                )
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
        required_fields = ["name", "lastname", "total", "cartera_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Campo requerido: {field}", field=field)
        
        # nro_cliente es opcional

        # Validar que cartera_id exista y esté activa
        cartera = Cartera.query.filter_by(id=data["cartera_id"], activo=True).first()
        if not cartera:
            raise ValidationError("Cartera no encontrada o inactiva", field="cartera_id")

        # Validar status_id (default: 1 = "Sin Arreglo")
        status_id = data.get("status_id", 1)
        status_obj = CaseStatus.query.filter_by(id=status_id, activo=True).first()
        if not status_obj:
            raise ValidationError("Estado no encontrado o inactivo", field="status_id")

        # Parsear fecha_ultimo_pago si viene como string
        fecha_ultimo_pago = data.get("fecha_ultimo_pago")
        if fecha_ultimo_pago and isinstance(fecha_ultimo_pago, str):
            from datetime import datetime
            try:
                fecha_ultimo_pago = datetime.fromisoformat(fecha_ultimo_pago.replace('Z', '+00:00')).date()
            except:
                fecha_ultimo_pago = None

        case = Case(
            name=data["name"],
            lastname=data["lastname"],
            dni=data.get("dni"),
            nro_cliente=data.get("nro_cliente"),
            total=data["total"],
            monto_inicial=data.get("monto_inicial"),
            fecha_ultimo_pago=fecha_ultimo_pago,
            telefono=data.get("telefono"),
            calle_nombre=data.get("calle_nombre"),
            calle_nro=data.get("calle_nro"),
            localidad=data.get("localidad"),
            cp=data.get("cp"),
            provincia=data.get("provincia"),
            status_id=status_id,
            cartera_id=data["cartera_id"],
            assigned_to_id=data.get("assigned_to_id"),
            notes=data.get("notes"),
        )

        db.session.add(case)
        db.session.commit()

        # Invalidar cache relacionado
        invalidate_cache("cache:dashboard:*")
        invalidate_cache("cache:kpis:*")

        audit_log("create_case", {"case_id": case.id, "name": case.name, "lastname": case.lastname, "total": float(case.total)})

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
        if "name" in data:
            case.name = data["name"]
        if "lastname" in data:
            case.lastname = data["lastname"]
        if "dni" in data:
            case.dni = data["dni"]
        if "nro_cliente" in data:
            case.nro_cliente = data["nro_cliente"]
        if "total" in data:
            case.total = data["total"]
        if "monto_inicial" in data:
            case.monto_inicial = data["monto_inicial"]
        if "telefono" in data:
            case.telefono = data["telefono"]
        if "calle_nombre" in data:
            case.calle_nombre = data["calle_nombre"]
        if "calle_nro" in data:
            case.calle_nro = data["calle_nro"]
        if "localidad" in data:
            case.localidad = data["localidad"]
        if "cp" in data:
            case.cp = data["cp"]
        if "provincia" in data:
            case.provincia = data["provincia"]
        if "status_id" in data:
            status_obj = CaseStatus.query.filter_by(id=data["status_id"], activo=True).first()
            if not status_obj:
                raise ValidationError("Estado no encontrado o inactivo", field="status_id")
            case.status_id = data["status_id"]
        if "fecha_ultimo_pago" in data:
            fecha_ultimo_pago = data["fecha_ultimo_pago"]
            if fecha_ultimo_pago and isinstance(fecha_ultimo_pago, str):
                from datetime import datetime
                try:
                    fecha_ultimo_pago = datetime.fromisoformat(fecha_ultimo_pago.replace('Z', '+00:00')).date()
                except:
                    fecha_ultimo_pago = None
            case.fecha_ultimo_pago = fecha_ultimo_pago
        if "cartera_id" in data:
            case.cartera_id = data["cartera_id"]
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

        # Mapear estados del frontend a IDs de estados en la BD
        status_name_map = {
            "sin-gestion": "Sin Arreglo",
            "en-gestion": "En gestión",
            "contactado": "Contactado",
            "con-arreglo": "Con Arreglo",
            "incobrable": "Incobrable",
            "a-juicio": "A Juicio",
            "de-baja": "De baja",
        }
        
        # Obtener el nombre del estado desde el mapeo
        status_nombre = status_name_map.get(status, "Sin Arreglo")
        
        # Buscar el estado en la BD
        status_obj = CaseStatus.query.filter_by(nombre=status_nombre, activo=True).first()
        if not status_obj:
            return jsonify({"success": False, "error": f"Estado '{status_nombre}' no encontrado"}), 400

        old_status_id = case.status_id
        old_status_nombre = case.status_rel.nombre if case.status_rel else None

        # Actualizar status_id
        case.status_id = status_obj.id
        db.session.commit()

        # Invalidar cache
        invalidate_cache("cache:dashboard:*")
        invalidate_cache("cache:kpis:*")

        audit_log(
            "update_case_status",
            {
                "case_id": case_id,
                "old_status_id": old_status_id,
                "old_status_nombre": old_status_nombre,
                "new_status_id": status_obj.id,
                "new_status_nombre": status_obj.nombre,
            },
        )

        app.logger.info(
            f"Estado actualizado: Caso {case_id} de '{old_status_nombre}' (ID: {old_status_id}) a '{status_obj.nombre}' (ID: {status_obj.id})"
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

            # Mapear nombre de estado de BD a código del frontend
            status_nombre_to_frontend = {
                "Sin Arreglo": "sin-gestion",
                "En gestión": "contactado",
                "Contactado": "contactado",
                "Con Arreglo": "con-arreglo",
                "Incobrable": "incobrable",
                "A Juicio": "con-arreglo",
                "De baja": "de-baja",
            }
            status_nombre = case.status_rel.nombre if case.status_rel else "Sin Arreglo"
            frontend_status = status_nombre_to_frontend.get(status_nombre, "sin-gestion")

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
        # Si es gestor, solo sus casos asignados (no ve casos sin asignar)
        query = Case.query
        if user_role == "gestor":
            query = query.filter(Case.assigned_to_id == user_id)

        # Filtros opcionales
        cartera_id = request.args.get("cartera_id", type=int)
        if cartera_id:
            query = query.filter(Case.cartera_id == cartera_id)

        status = request.args.get("status")
        if status:
            # status puede ser un ID o un nombre de estado
            try:
                status_id = int(status)
                query = query.filter(Case.status_id == status_id)
            except ValueError:
                # Es un nombre, buscar por nombre
                status_obj = CaseStatus.query.filter_by(nombre=status, activo=True).first()
                if status_obj:
                    query = query.filter(Case.status_id == status_obj.id)

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


@bp.route("/cases/multiples-deudas")
@require_role("admin")
def get_casos_multiples_deudas():
    """
    Obtiene clientes con múltiples deudas agrupados por DNI.
    Usa SQL GROUP BY para eficiencia. Útil para reportes y dashboard admin.
    """
    try:
        cartera_id = request.args.get("cartera_id", type=int)
        gestor_id = request.args.get("gestor_id", type=int)
        
        clientes = get_clientes_con_multiples_deudas(
            cartera_id=cartera_id,
            gestor_id=gestor_id
        )
        
        return jsonify({
            "success": True,
            "data": clientes,
            "total": len(clientes)
        })
    except Exception as e:
        app.logger.error(f"Error obteniendo clientes con múltiples deudas: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cases/gestor/agrupados")
def get_gestor_cases_agrupados():
    """
    Obtiene casos del gestor agrupados por DNI.
    Retorna estructura: [{ dni, cliente, deudas[], total_deudas, deuda_consolidada }]
    """
    try:
        user_id = session.get("user_id")
        user_role = session.get("role")
        
        if not user_id:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
        
        # Filtros opcionales
        cartera_id = request.args.get("cartera_id", type=int)
        include_relations = request.args.get("include_relations", "false").lower() == "true"
        
        # Obtener casos agrupados por DNI
        grupos = get_casos_agrupados_por_dni(
            cartera_id=cartera_id,
            gestor_id=user_id if user_role == "gestor" else None,
            include_relations=include_relations
        )
        
        return jsonify({
            "success": True,
            "data": grupos,
            "total_grupos": len(grupos),
            "total_deudas": sum(g["total_deudas"] for g in grupos)
        })
    except Exception as e:
        app.logger.error(f"Error obteniendo casos agrupados: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
