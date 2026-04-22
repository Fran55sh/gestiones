"""
Utilidades para importación de casos desde CSV (admin).
"""

from __future__ import annotations

import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Tuple

# Límite de tamaño de archivo (5 MB)
MAX_IMPORT_FILE_BYTES = 5 * 1024 * 1024
# Máximo de filas de datos (sin contar encabezado)
MAX_IMPORT_ROWS = 5000

# Encabezados esperados (orden para plantilla descargable)
CSV_TEMPLATE_HEADERS = [
    "name",
    "lastname",
    "total",
    "cartera_id",
    "cartera_nombre",
    "monto_inicial",
    "dni",
    "nro_cliente",
    "telefono",
    "calle_nombre",
    "calle_nro",
    "localidad",
    "cp",
    "provincia",
    "fecha_ultimo_pago",
    "notes",
    "status_id",
    "assigned_to_id",
]


def csv_template_body() -> str:
    """Una línea de encabezados; cartera_id o cartera_nombre (al menos uno requerido por fila)."""
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(CSV_TEMPLATE_HEADERS)
    return buf.getvalue()


def _normalize_row_keys(row: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in row.items():
        if k is None:
            continue
        key = str(k).strip().lower()
        if v is None:
            out[key] = ""
        else:
            out[key] = str(v).strip()
    return out


def parse_amount(amount_str: Optional[str]) -> Optional[Decimal]:
    """Parsea monto desde string (compatible con formatos con coma/punto)."""
    if not amount_str or not str(amount_str).strip():
        return None
    cleaned = str(amount_str).replace("$", "").replace(" ", "").strip()
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            cleaned = parts[0] + "." + parts[1]
        else:
            cleaned = cleaned.replace(",", "")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def parse_date_flexible(date_str: Optional[str]):
    """Retorna date o None. Acepta DD/MM/YYYY, MM/DD/YYYY ambiguos, YYYY-MM-DD."""
    if not date_str or not str(date_str).strip():
        return None
    s = str(date_str).strip()
    try:
        if len(s) >= 10 and s[4] == "-" and s[7] == "-":
            return datetime.fromisoformat(s[:10]).date()
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%m/%d/%Y").date()
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _get(row: Dict[str, str], *keys: str) -> str:
    for k in keys:
        if k in row and row[k] != "":
            return row[k]
    return ""


def parse_cases_csv(file_stream) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Procesa un archivo CSV subido. Inserta fila a fila (commit por fila).

    Returns:
        imported, skipped, errors (lista de {row: int, message: str})
    """
    from ..core.database import db
    from ..features.cases.models import Case, CaseStatus
    from ..features.carteras.models import Cartera

    session = db.session
    raw = file_stream.read()
    if len(raw) > MAX_IMPORT_FILE_BYTES:
        return 0, 0, [{"row": 0, "message": f"Archivo demasiado grande (máx. {MAX_IMPORT_FILE_BYTES // (1024 * 1024)} MB)"}]

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = raw.decode("latin-1")
        except UnicodeDecodeError:
            return 0, 0, [{"row": 0, "message": "No se pudo decodificar el archivo (use UTF-8)"}]

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return 0, 0, [{"row": 0, "message": "CSV vacío o sin encabezados"}]

    imported = 0
    skipped = 0
    errors: List[Dict[str, Any]] = []
    row_index = 1  # línea de encabezado

    for raw_row in reader:
        row_index += 1
        if row_index - 1 > MAX_IMPORT_ROWS:
            errors.append({"row": row_index, "message": f"Límite de {MAX_IMPORT_ROWS} filas excedido"})
            break

        row = _normalize_row_keys(raw_row)

        name = _get(row, "name", "nombre")
        lastname = _get(row, "lastname", "apellido")
        total_s = _get(row, "total")

        if not name or not lastname:
            errors.append({"row": row_index, "message": "Faltan name y/o lastname"})
            continue

        total_dec = parse_amount(total_s)
        if total_dec is None or total_dec < 0:
            errors.append({"row": row_index, "message": "total inválido o faltante"})
            continue

        cartera_id_s = _get(row, "cartera_id")
        cartera_nombre = _get(row, "cartera_nombre")

        cartera = None
        if cartera_id_s:
            try:
                cid = int(cartera_id_s)
                cartera = Cartera.query.filter_by(id=cid, activo=True).first()
            except ValueError:
                errors.append({"row": row_index, "message": "cartera_id inválido"})
                continue
        if cartera is None and cartera_nombre:
            cartera = Cartera.query.filter_by(nombre=cartera_nombre.strip(), activo=True).first()

        if cartera is None:
            errors.append({"row": row_index, "message": "Cartera no encontrada o inactiva (use cartera_id o cartera_nombre)"})
            continue

        nro_cliente = _get(row, "nro_cliente") or None
        if nro_cliente:
            existing = Case.query.filter_by(nro_cliente=nro_cliente).first()
            if existing:
                skipped += 1
                continue

        status_id = 1
        status_s = _get(row, "status_id")
        if status_s:
            try:
                status_id = int(status_s)
            except ValueError:
                errors.append({"row": row_index, "message": "status_id inválido"})
                continue
        status_obj = CaseStatus.query.filter_by(id=status_id, activo=True).first()
        if not status_obj:
            errors.append({"row": row_index, "message": f"Estado id={status_id} no encontrado o inactivo"})
            continue

        assigned_to_id = None
        as_s = _get(row, "assigned_to_id", "assigned_to")
        if as_s:
            try:
                assigned_to_id = int(as_s)
            except ValueError:
                errors.append({"row": row_index, "message": "assigned_to_id inválido"})
                continue

        monto_inicial = parse_amount(_get(row, "monto_inicial"))
        fecha_ultimo_pago = parse_date_flexible(_get(row, "fecha_ultimo_pago"))

        try:
            case = Case(
                name=name,
                lastname=lastname,
                dni=_get(row, "dni") or None,
                nro_cliente=nro_cliente,
                total=total_dec,
                monto_inicial=monto_inicial,
                fecha_ultimo_pago=fecha_ultimo_pago,
                telefono=_get(row, "telefono") or None,
                calle_nombre=_get(row, "calle_nombre", "calle") or None,
                calle_nro=_get(row, "calle_nro") or None,
                localidad=_get(row, "localidad") or None,
                cp=_get(row, "cp") or None,
                provincia=_get(row, "provincia", "ptovincia") or None,
                status_id=status_id,
                cartera_id=cartera.id,
                assigned_to_id=assigned_to_id,
                notes=_get(row, "notes") or None,
            )
            session.add(case)
            session.commit()
            imported += 1
        except Exception as e:
            session.rollback()
            errors.append({"row": row_index, "message": str(e)[:500]})

    return imported, skipped, errors
