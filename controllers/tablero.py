"""
controllers/tablero.py - Controlador para la vista del tablero principal (ruta /).
No realiza cálculos: delega a models.certificados.
"""
from flask import Blueprint, render_template, request
from models.certificados import procesar_reglas_negocio

tablero_bp = Blueprint("tablero", __name__)


@tablero_bp.route("/")
@tablero_bp.route("/tablero")
@tablero_bp.route("/index")
@tablero_bp.route("/index.html")
@tablero_bp.route("/home")
def index():
    """Ruta principal del tablero: muestra estadísticas, tabla y alertas."""
    try:
        datos = procesar_reglas_negocio()
        error = None
    except Exception as e:
        datos = {
            "contadores": {"aprobacion": 0, "participacion": 0, "sin_certificado": 0, "inconsistencias": 0},
            "estudiantes": [],
            "inconsistencias": [],
        }
        error = f"Error al procesar los datos: {str(e)}"

    # Filtro por programa: solo decide qué filas se muestran, los contadores siguen globales.
    programas = sorted({e["programa"] for e in datos["estudiantes"]})
    programa_actual = (request.args.get("programa") or "").strip()
    if programa_actual in programas:
        estudiantes = [e for e in datos["estudiantes"] if e["programa"] == programa_actual]
    else:
        programa_actual = ""
        estudiantes = datos["estudiantes"]

    return render_template(
        "tablero.html",
        contadores=datos["contadores"],
        estudiantes=estudiantes,
        inconsistencias=datos["inconsistencias"],
        programas=programas,
        programa_actual=programa_actual,
        error=error,
    )
