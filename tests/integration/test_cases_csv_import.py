"""
Tests importación masiva CSV de casos (admin).
"""

import io

import pytest

from app.core.database import db
from app.features.carteras.models import Cartera
from app.features.cases.models import Case, CaseStatus


@pytest.fixture(autouse=True)
def seed_cartera_y_estados(app):
    """En TESTING no se ejecutan los seeds de create_app; datos mínimos para import."""
    with app.app_context():
        if Cartera.query.filter_by(nombre="Cristal Cash").first() is None:
            db.session.add(Cartera(nombre="Cristal Cash", activo=True))
        if CaseStatus.query.filter_by(nombre="Sin Arreglo").first() is None:
            db.session.add(CaseStatus(nombre="Sin Arreglo", activo=True))
        db.session.commit()


def test_import_template_requires_auth(client):
    """Sin sesión admin, la plantilla no debe entregarse como éxito API."""
    r = client.get("/api/cases/import-template")
    assert r.status_code in (302, 401)


def test_import_template_authenticated(authenticated_client):
    r = authenticated_client.get("/api/cases/import-template")
    assert r.status_code == 200
    assert "name" in r.data.decode("utf-8-sig")
    assert "lastname" in r.data.decode("utf-8-sig")
    assert "total" in r.data.decode("utf-8-sig")


def test_import_csv_two_rows(authenticated_client, app):
    """Importa dos filas válidas."""
    with app.app_context():
        cartera = Cartera.query.filter_by(nombre="Cristal Cash", activo=True).first()
        assert cartera is not None

    csv_content = (
        "name,lastname,total,cartera_nombre\n"
        "Juan,Perez,1000.50,Cristal Cash\n"
        "Maria,Gomez,2000,Cristal Cash\n"
    )
    r = authenticated_client.post(
        "/api/cases/import",
        data={"file": (io.BytesIO(csv_content.encode("utf-8")), "casos.csv")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert data["imported"] == 2
    assert data["skipped"] == 0


def test_import_csv_skips_duplicate_nro_cliente(authenticated_client, app):
    """Si nro_cliente ya existe, la fila se omite."""
    with app.app_context():
        cartera = Cartera.query.filter_by(nombre="Cristal Cash", activo=True).first()
        st = CaseStatus.query.filter_by(nombre="Sin Arreglo", activo=True).first()
        c = Case(
            name="Existente",
            lastname="Cliente",
            nro_cliente="NC-DUP-1",
            total=500,
            cartera_id=cartera.id,
            status_id=st.id,
        )
        db.session.add(c)
        db.session.commit()

    csv_content = (
        "name,lastname,total,cartera_nombre,nro_cliente\n"
        "Otro,Nombre,9999,Cristal Cash,NC-DUP-1\n"
        "Nuevo,SinDup,100,Cristal Cash,NC-NEW-2\n"
    )
    r = authenticated_client.post(
        "/api/cases/import",
        data={"file": (io.BytesIO(csv_content.encode("utf-8")), "dup.csv")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert data["skipped"] == 1
    assert data["imported"] == 1


def test_import_csv_column_aliases_calle_ptovincia_assigned_to(authenticated_client, app):
    """Acepta calle→calle_nombre, ptovincia→provincia, assigned_to→assigned_to_id."""
    with app.app_context():
        cartera = Cartera.query.filter_by(nombre="Cristal Cash", activo=True).first()
        assert cartera is not None

    csv_content = (
        "name,lastname,total,cartera_nombre,calle,ptovincia,assigned_to\n"
        "Alias,Test,100,Cristal Cash,San Martín,Buenos Aires,2\n"
    )
    r = authenticated_client.post(
        "/api/cases/import",
        data={"file": (io.BytesIO(csv_content.encode("utf-8")), "aliases.csv")},
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert data["imported"] == 1

    with app.app_context():
        c = Case.query.filter_by(name="Alias", lastname="Test").first()
        assert c is not None
        assert c.calle_nombre == "San Martín"
        assert c.provincia == "Buenos Aires"
        assert c.assigned_to_id == 2
