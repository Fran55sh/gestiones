"""
Servicio para agregación de datos del dashboard.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy import func

from ..core.database import db
from ..features.cases.models import Case, CaseStatus
from ..features.cases.promise import Promise
from ..features.activities.models import Activity
from ..features.users.models import User
from ..features.carteras.models import Cartera
from .cache import cache_result


@cache_result(timeout=300, key_prefix="kpis")
def get_kpis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    cartera_id: Optional[int] = None,
    gestor_id: Optional[int] = None,
) -> Dict:
    """
    Calcula los KPIs principales del dashboard.

    Args:
        start_date: Fecha de inicio del período
        end_date: Fecha de fin del período
        cartera_id: Filtro por cartera (ID)
        gestor_id: Filtro por gestor

    Returns:
        Diccionario con KPIs
    """
    # Construir query base
    query = Case.query

    # Aplicar filtros
    if start_date:
        query = query.filter(Case.created_at >= start_date)
    if end_date:
        query = query.filter(Case.created_at <= end_date)
    if cartera_id:
        query = query.filter(Case.cartera_id == cartera_id)
    if gestor_id:
        query = query.filter(Case.assigned_to_id == gestor_id)

    # Monto total recuperado (casos con arreglo - estado "Con Arreglo")
    # Buscar estado "Con Arreglo" por nombre
    con_arreglo_status = CaseStatus.query.filter_by(nombre="Con Arreglo", activo=True).first()
    if con_arreglo_status:
        paid_cases = query.filter(Case.status_id == con_arreglo_status.id).all()
    else:
        paid_cases = []
    monto_recuperado = sum(float(c.total) for c in paid_cases)

    # Monto total de deuda
    total_deuda = query.with_entities(func.sum(Case.total)).scalar() or Decimal("0")
    total_deuda_float = float(total_deuda)

    # Tasa de recupero
    tasa_recupero = (monto_recuperado / total_deuda_float * 100) if total_deuda_float > 0 else 0.0

    # Promesas cumplidas
    promises_query = Promise.query
    if start_date:
        promises_query = promises_query.filter(Promise.created_at >= start_date)
    if end_date:
        promises_query = promises_query.filter(Promise.created_at <= end_date)
    if gestor_id:
        # Filtrar promesas de casos del gestor
        case_ids = [c.id for c in query.filter(Case.assigned_to_id == gestor_id).all()]
        if case_ids:
            promises_query = promises_query.filter(Promise.case_id.in_(case_ids))
        else:
            promises_query = promises_query.filter(False)  # No hay casos, no hay promesas

    total_promises = promises_query.count()
    fulfilled_promises = promises_query.filter(Promise.status == "fulfilled").count()
    promesas_cumplidas_pct = (fulfilled_promises / total_promises * 100) if total_promises > 0 else 0.0

    # Gestiones realizadas (actividades)
    activities_query = Activity.query
    if start_date:
        activities_query = activities_query.filter(Activity.created_at >= start_date)
    if end_date:
        activities_query = activities_query.filter(Activity.created_at <= end_date)
    if gestor_id:
        activities_query = activities_query.filter(Activity.created_by_id == gestor_id)
    if cartera_id or gestor_id:
        # Filtrar por casos
        case_ids = [c.id for c in query.all()]
        if case_ids:
            activities_query = activities_query.filter(Activity.case_id.in_(case_ids))
        else:
            activities_query = activities_query.filter(False)

    gestiones_realizadas = activities_query.count()

    return {
        "monto_recuperado": round(monto_recuperado, 2),
        "tasa_recupero": round(tasa_recupero, 2),
        "promesas_cumplidas": round(promesas_cumplidas_pct, 2),
        "gestiones_realizadas": gestiones_realizadas,
        "total_casos": query.count(),
        "casos_pagados": len(paid_cases),
        "total_deuda": round(total_deuda_float, 2),
    }


@cache_result(timeout=300, key_prefix="performance_chart")
def get_performance_chart_data(
    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, cartera_id: Optional[int] = None
) -> Dict:
    """
    Obtiene datos para el gráfico de rendimiento por semana y cartera.

    Returns:
        Diccionario con datos para Chart.js
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=28)  # Últimas 4 semanas
    if not end_date:
        end_date = datetime.utcnow()

    # Dividir en semanas
    weeks = []
    current = start_date
    while current < end_date:
        week_end = min(current + timedelta(days=7), end_date)
        weeks.append((current, week_end))
        current = week_end

    # Obtener todas las carteras activas desde la tabla carteras
    carteras = Cartera.query.filter_by(activo=True).order_by(Cartera.nombre).limit(5).all()

    # Datos por semana y cartera
    datasets = []
    colors = ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"]

    for idx, cartera in enumerate(carteras):
        if cartera_id and cartera.id != cartera_id:
            continue
        data = []
        for week_start, week_end in weeks:
            # Buscar estado "Con Arreglo" para casos pagados
            con_arreglo_status = CaseStatus.query.filter_by(nombre="Con Arreglo", activo=True).first()
            if con_arreglo_status:
                query = Case.query.filter(
                    Case.cartera_id == cartera.id,
                    Case.created_at >= week_start,
                    Case.created_at < week_end,
                    Case.status_id == con_arreglo_status.id,
                )
            else:
                query = Case.query.filter(False)  # No hay estado, no hay datos
            total = query.with_entities(func.sum(Case.total)).scalar() or Decimal("0")
            data.append(float(total))

        datasets.append({"label": cartera.nombre, "data": data, "backgroundColor": colors[idx % len(colors)]})

    labels = [f"Sem {i+1}" for i in range(len(weeks))]

    return {"labels": labels, "datasets": datasets}


@cache_result(timeout=600, key_prefix="cartera_distribution")
def get_cartera_distribution() -> Dict:
    """
    Obtiene distribución de casos por cartera.

    Returns:
        Diccionario con datos para gráfico de dona
    """
    result = db.session.query(
        Cartera.nombre,
        func.sum(Case.total).label("total")
    ).join(Case, Cartera.id == Case.cartera_id).group_by(Cartera.id, Cartera.nombre).all()

    labels = [r[0] for r in result]
    data = [float(r[1]) for r in result]

    colors = ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"]

    return {"labels": labels, "datasets": [{"data": data, "backgroundColor": colors[: len(labels)]}]}


@cache_result(timeout=300, key_prefix="gestores_ranking")
def get_gestores_ranking(limit: int = 10) -> List[Dict]:
    """
    Obtiene ranking de gestores por monto recuperado.

    Args:
        limit: Número máximo de gestores a retornar

    Returns:
        Lista de gestores con sus métricas
    """
    gestores = User.query.filter(User.role == "gestor", User.active.is_(True)).all()

    ranking = []
    # Buscar estado "Con Arreglo" para casos pagados
    con_arreglo_status = CaseStatus.query.filter_by(nombre="Con Arreglo", activo=True).first()
    for gestor in gestores:
        if con_arreglo_status:
            cases = Case.query.filter(Case.assigned_to_id == gestor.id, Case.status_id == con_arreglo_status.id).all()
        else:
            cases = []

        monto_recuperado = sum(float(c.total) for c in cases)
        total_casos = Case.query.filter(Case.assigned_to_id == gestor.id).count()
        casos_pagados = len(cases)

        # Promesas cumplidas
        case_ids = [c.id for c in Case.query.filter(Case.assigned_to_id == gestor.id).all()]
        if case_ids:
            total_promises = Promise.query.filter(Promise.case_id.in_(case_ids)).count()
            fulfilled_promises = Promise.query.filter(Promise.case_id.in_(case_ids), Promise.status == "fulfilled").count()
            promesas_cumplidas_pct = (fulfilled_promises / total_promises * 100) if total_promises > 0 else 0.0
        else:
            promesas_cumplidas_pct = 0.0

        ranking.append(
            {
                "gestor_id": gestor.id,
                "gestor_name": gestor.username,
                "monto_recuperado": round(monto_recuperado, 2),
                "total_casos": total_casos,
                "casos_pagados": casos_pagados,
                "promesas_cumplidas": round(promesas_cumplidas_pct, 2),
            }
        )

    # Ordenar por monto recuperado
    ranking.sort(key=lambda x: x["monto_recuperado"], reverse=True)

    return ranking[:limit]


def get_cases_status_distribution() -> Dict:
    """
    Obtiene distribución de casos por estado.

    Returns:
        Diccionario con conteos por estado
    """
    # Obtener todos los estados activos
    statuses = CaseStatus.query.filter_by(activo=True).all()
    distribution = {}

    for status in statuses:
        count = Case.query.filter(Case.status_id == status.id).count()
        distribution[status.nombre] = count

    return distribution


def get_comparison_data() -> Dict:
    """
    Obtiene datos comparativos entre mes actual y anterior.

    Returns:
        Diccionario con datos comparativos
    """
    now = datetime.utcnow()
    current_month_start = datetime(now.year, now.month, 1)
    if now.month == 1:
        previous_month_start = datetime(now.year - 1, 12, 1)
        previous_month_end = datetime(now.year, 1, 1)
    else:
        previous_month_start = datetime(now.year, now.month - 1, 1)
        previous_month_end = datetime(now.year, now.month, 1)

    # Mes actual
    con_arreglo_status = CaseStatus.query.filter_by(nombre="Con Arreglo", activo=True).first()
    if con_arreglo_status:
        current_cases = Case.query.filter(Case.created_at >= current_month_start, Case.status_id == con_arreglo_status.id).all()
    else:
        current_cases = []
    current_monto = sum(float(c.total) for c in current_cases)

    current_promises = Promise.query.filter(Promise.created_at >= current_month_start).all()
    current_fulfilled = sum(1 for p in current_promises if p.status == "fulfilled")
    current_promises_pct = (current_fulfilled / len(current_promises) * 100) if current_promises else 0.0

    current_activities = Activity.query.filter(Activity.created_at >= current_month_start).count()

    # Mes anterior
    if con_arreglo_status:
        previous_cases = Case.query.filter(
            Case.created_at >= previous_month_start, Case.created_at < previous_month_end, Case.status_id == con_arreglo_status.id
        ).all()
    else:
        previous_cases = []
    previous_monto = sum(float(c.total) for c in previous_cases)

    previous_promises = Promise.query.filter(
        Promise.created_at >= previous_month_start, Promise.created_at < previous_month_end
    ).all()
    previous_fulfilled = sum(1 for p in previous_promises if p.status == "fulfilled")
    previous_promises_pct = (previous_fulfilled / len(previous_promises) * 100) if previous_promises else 0.0

    previous_activities = Activity.query.filter(
        Activity.created_at >= previous_month_start, Activity.created_at < previous_month_end
    ).count()

    return {
        "current": {
            "monto_recuperado": round(current_monto, 2),
            "promesas_cumplidas": round(current_promises_pct, 2),
            "gestiones_realizadas": current_activities,
        },
        "previous": {
            "monto_recuperado": round(previous_monto, 2),
            "promesas_cumplidas": round(previous_promises_pct, 2),
            "gestiones_realizadas": previous_activities,
        },
    }


@cache_result(timeout=600, key_prefix="clientes_multiples_deudas")
def get_clientes_con_multiples_deudas(
    cartera_id: Optional[int] = None,
    gestor_id: Optional[int] = None,
) -> List[Dict]:
    """
    Obtiene clientes (por DNI) que tienen más de una deuda usando SQL GROUP BY.
    Optimizado para grandes volúmenes de datos.

    Args:
        cartera_id: Filtro opcional por cartera
        gestor_id: Filtro opcional por gestor

    Returns:
        Lista de diccionarios con información consolidada por DNI
    """
    # Construir query base con GROUP BY
    query = db.session.query(
        Case.dni,
        func.count(Case.id).label('total_deudas'),
        func.sum(Case.total).label('deuda_consolidada'),
        func.max(Case.fecha_ultimo_pago).label('fecha_mas_reciente'),
        func.min(Case.created_at).label('primera_deuda'),
        func.max(Case.created_at).label('ultima_deuda'),
        func.sum(Case.monto_inicial).label('monto_inicial_total'),
    ).filter(
        Case.dni.isnot(None)  # Excluir casos sin DNI
    )
    
    # Aplicar filtros
    if cartera_id:
        query = query.filter(Case.cartera_id == cartera_id)
    if gestor_id:
        query = query.filter(Case.assigned_to_id == gestor_id)
    
    # Agrupar por DNI y filtrar solo los que tienen más de una deuda
    result = query.group_by(
        Case.dni
    ).having(
        func.count(Case.id) > 1
    ).order_by(
        func.sum(Case.total).desc()
    ).all()
    
    return [
        {
            'dni': r.dni,
            'total_deudas': r.total_deudas,
            'deuda_consolidada': float(r.deuda_consolidada) if r.deuda_consolidada else 0.0,
            'monto_inicial_total': float(r.monto_inicial_total) if r.monto_inicial_total else 0.0,
            'fecha_mas_reciente': r.fecha_mas_reciente.isoformat() if r.fecha_mas_reciente else None,
            'primera_deuda': r.primera_deuda.isoformat() if r.primera_deuda else None,
            'ultima_deuda': r.ultima_deuda.isoformat() if r.ultima_deuda else None,
        }
        for r in result
    ]


def get_casos_agrupados_por_dni(
    cartera_id: Optional[int] = None,
    gestor_id: Optional[int] = None,
    include_relations: bool = False,
) -> List[Dict]:
    """
    Obtiene casos agrupados por DNI para el frontend.
    Cada grupo contiene los datos del cliente y todas sus deudas.
    
    IMPORTANTE: Si se filtra por cartera_id, se muestran TODAS las deudas del cliente,
    pero solo se retornan grupos que tengan al menos una deuda en esa cartera.

    Args:
        cartera_id: Filtro opcional por cartera (solo filtra qué grupos mostrar, no las deudas dentro)
        gestor_id: Filtro opcional por gestor
        include_relations: Si incluir relaciones (promises, activities)

    Returns:
        Lista de grupos, cada uno con dni, cliente y deudas
    """
    # Obtener TODOS los casos (sin filtrar por gestor ni cartera)
    # Esto es necesario para agrupar TODAS las deudas de cada cliente
    # Luego filtraremos qué grupos mostrar, pero mantendremos todas las deudas dentro de cada grupo
    query = Case.query
    todos_los_casos = query.order_by(Case.created_at.desc()).all()
    
    # Agrupar por DNI (incluyendo TODAS las deudas de cada cliente)
    grupos = {}
    for caso in todos_los_casos:
        dni = caso.dni or f"SIN-DNI-{caso.id}"
        
        if dni not in grupos:
            # Crear grupo nuevo con datos del cliente (del primer caso encontrado)
            grupos[dni] = {
                "dni": caso.dni,
                "cliente": {
                    "name": caso.name,
                    "lastname": caso.lastname,
                    "dni": caso.dni,
                    "telefono": caso.telefono,
                    "calle_nombre": caso.calle_nombre,
                    "calle_nro": caso.calle_nro,
                    "localidad": caso.localidad,
                    "provincia": caso.provincia,
                    "cp": caso.cp,
                },
                "deudas": [],
                "total_deudas": 0,
                "deuda_consolidada": 0.0,
                "monto_inicial_total": 0.0,
            }
        
        # Agregar esta deuda al grupo (TODAS las deudas, sin filtrar por cartera)
        deuda_dict = caso.to_dict(include_relations=include_relations)
        grupos[dni]["deudas"].append(deuda_dict)
        
        # Actualizar totales
        grupos[dni]["total_deudas"] += 1
        grupos[dni]["deuda_consolidada"] += float(caso.total) if caso.total else 0.0
        grupos[dni]["monto_inicial_total"] += float(caso.monto_inicial) if caso.monto_inicial else 0.0
    
    # Ordenar deudas dentro de cada grupo por fecha (más reciente primero)
    for grupo in grupos.values():
        grupo["deudas"].sort(
            key=lambda d: d.get("created_at") or d.get("id", 0) or "", 
            reverse=True
        )
    
    # Aplicar filtros para determinar qué grupos mostrar
    # Pero mantener TODAS las deudas dentro de cada grupo
    grupos_filtrados = []
    for grupo in grupos.values():
        # Verificar si el grupo cumple con los filtros
        cumple_filtros = True
        
        # Filtro por cartera: el grupo debe tener al menos una deuda en esa cartera
        if cartera_id:
            tiene_deuda_en_cartera = any(
                deuda.get("cartera_id") == cartera_id 
                for deuda in grupo["deudas"]
            )
            if not tiene_deuda_en_cartera:
                cumple_filtros = False
        
        # Filtro por gestor: el grupo debe tener al menos una deuda asignada a ese gestor
        if gestor_id and cumple_filtros:
            tiene_deuda_asignada = any(
                deuda.get("assigned_to_id") == gestor_id 
                for deuda in grupo["deudas"]
            )
            if not tiene_deuda_asignada:
                cumple_filtros = False
        
        if cumple_filtros:
            grupos_filtrados.append(grupo)
    
    return grupos_filtrados
