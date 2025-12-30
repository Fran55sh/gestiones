"""
Servicio para agregación de datos del dashboard.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy import func

from ..core.database import db
from ..models import Case, Promise, Activity, User
from ..utils.cache import cache_result


@cache_result(timeout=300, key_prefix="kpis")
def get_kpis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    cartera: Optional[str] = None,
    gestor_id: Optional[int] = None,
) -> Dict:
    """
    Calcula los KPIs principales del dashboard.

    Args:
        start_date: Fecha de inicio del período
        end_date: Fecha de fin del período
        cartera: Filtro por cartera
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
    if cartera:
        query = query.filter(Case.cartera == cartera)
    if gestor_id:
        query = query.filter(Case.assigned_to_id == gestor_id)

    # Monto total recuperado (casos pagados)
    paid_cases = query.filter(Case.status == "pagada").all()
    monto_recuperado = sum(float(c.amount) for c in paid_cases)

    # Monto total de deuda
    total_deuda = query.with_entities(func.sum(Case.amount)).scalar() or Decimal("0")
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
    if cartera or gestor_id:
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
    start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, cartera: Optional[str] = None
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

    # Obtener todas las carteras
    carteras = db.session.query(Case.cartera).distinct().all()
    carteras = [c[0] for c in carteras] if carteras else ["Cartera A", "Cartera B", "Cartera C"]

    # Datos por semana y cartera
    datasets = []
    colors = ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#00f2fe"]

    for idx, cartera_name in enumerate(carteras[:5]):  # Máximo 5 carteras
        data = []
        for week_start, week_end in weeks:
            query = Case.query.filter(
                Case.cartera == cartera_name,
                Case.created_at >= week_start,
                Case.created_at < week_end,
                Case.status == "pagada",
            )
            if cartera and cartera != cartera_name:
                continue
            total = query.with_entities(func.sum(Case.amount)).scalar() or Decimal("0")
            data.append(float(total))

        datasets.append({"label": cartera_name, "data": data, "backgroundColor": colors[idx % len(colors)]})

    labels = [f"Sem {i+1}" for i in range(len(weeks))]

    return {"labels": labels, "datasets": datasets}


@cache_result(timeout=600, key_prefix="cartera_distribution")
def get_cartera_distribution() -> Dict:
    """
    Obtiene distribución de casos por cartera.

    Returns:
        Diccionario con datos para gráfico de dona
    """
    result = db.session.query(Case.cartera, func.sum(Case.amount).label("total")).group_by(Case.cartera).all()

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
    for gestor in gestores:
        cases = Case.query.filter(Case.assigned_to_id == gestor.id, Case.status == "pagada").all()

        monto_recuperado = sum(float(c.amount) for c in cases)
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
    statuses = ["en_gestion", "promesa", "pagada", "incobrable"]
    distribution = {}

    for status in statuses:
        count = Case.query.filter(Case.status == status).count()
        distribution[status] = count

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
    current_cases = Case.query.filter(Case.created_at >= current_month_start, Case.status == "pagada").all()
    current_monto = sum(float(c.amount) for c in current_cases)

    current_promises = Promise.query.filter(Promise.created_at >= current_month_start).all()
    current_fulfilled = sum(1 for p in current_promises if p.status == "fulfilled")
    current_promises_pct = (current_fulfilled / len(current_promises) * 100) if current_promises else 0.0

    current_activities = Activity.query.filter(Activity.created_at >= current_month_start).count()

    # Mes anterior
    previous_cases = Case.query.filter(
        Case.created_at >= previous_month_start, Case.created_at < previous_month_end, Case.status == "pagada"
    ).all()
    previous_monto = sum(float(c.amount) for c in previous_cases)

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
