"""
Tests para servicios del dashboard.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.core.database import db
from app.models import User, Case, Promise, Activity
from app.services.dashboard_service import (
    get_kpis,
    get_performance_chart_data,
    get_cartera_distribution,
    get_gestores_ranking,
    get_cases_status_distribution,
    get_comparison_data,
)


@pytest.fixture
def sample_data(app):
    """Crea datos de muestra para tests."""
    with app.app_context():
        # Usar el gestor ya creado en conftest
        gestor = User.query.filter_by(username="gestor").first()

        # Crear casos
        case1 = Case(
            entity="Entity 1",
            debtor_name="Debtor 1",
            amount=Decimal("10000.00"),
            status="pagada",
            cartera="Cartera A",
            assigned_to_id=gestor.id,
        )
        case2 = Case(
            entity="Entity 2",
            debtor_name="Debtor 2",
            amount=Decimal("5000.00"),
            status="en_gestion",
            cartera="Cartera B",
            assigned_to_id=gestor.id,
        )
        db.session.add_all([case1, case2])
        db.session.commit()

        # Crear promesa
        promise = Promise(case_id=case1.id, amount=Decimal("5000.00"), promise_date=datetime.now().date(), status="fulfilled")
        db.session.add(promise)

        # Crear actividad
        activity = Activity(case_id=case1.id, type="call", notes="Test call", created_by_id=gestor.id)
        db.session.add(activity)
        db.session.commit()

        return {"gestor": gestor, "case1": case1, "case2": case2, "promise": promise, "activity": activity}


def test_get_kpis(app, sample_data):
    """Test cálculo de KPIs."""
    with app.app_context():
        kpis = get_kpis()

        assert "monto_recuperado" in kpis
        assert "tasa_recupero" in kpis
        assert "promesas_cumplidas" in kpis
        assert "gestiones_realizadas" in kpis
        assert isinstance(kpis["monto_recuperado"], (int, float))
        assert isinstance(kpis["tasa_recupero"], (int, float))


def test_get_kpis_with_filters(app, sample_data):
    """Test KPIs con filtros."""
    with app.app_context():
        kpis = get_kpis(cartera="Cartera A")
        assert "monto_recuperado" in kpis

        kpis_gestor = get_kpis(gestor_id=sample_data["gestor"].id)
        assert "monto_recuperado" in kpis_gestor


def test_get_performance_chart_data(app, sample_data):
    """Test datos de gráfico de rendimiento."""
    with app.app_context():
        data = get_performance_chart_data()

        assert "labels" in data
        assert "datasets" in data
        assert isinstance(data["labels"], list)
        assert isinstance(data["datasets"], list)


def test_get_cartera_distribution(app, sample_data):
    """Test distribución por cartera."""
    with app.app_context():
        data = get_cartera_distribution()

        assert "labels" in data
        assert "datasets" in data
        assert len(data["labels"]) > 0


def test_get_gestores_ranking(app, sample_data):
    """Test ranking de gestores."""
    with app.app_context():
        ranking = get_gestores_ranking()

        assert isinstance(ranking, list)
        if len(ranking) > 0:
            assert "gestor_name" in ranking[0]
            assert "monto_recuperado" in ranking[0]


def test_get_cases_status_distribution(app, sample_data):
    """Test distribución de estados."""
    with app.app_context():
        distribution = get_cases_status_distribution()

        assert "en_gestion" in distribution
        assert "pagada" in distribution
        assert "promesa" in distribution
        assert "incobrable" in distribution


def test_get_comparison_data(app, sample_data):
    """Test datos comparativos."""
    with app.app_context():
        data = get_comparison_data()

        assert "current" in data
        assert "previous" in data
        assert "monto_recuperado" in data["current"]
        assert "promesas_cumplidas" in data["current"]
