"""
controllers/cargas.py - Controlador para la carga web de los archivos Excel (ruta /cargar).
No procesa archivos directamente: delega a services.carga_excel.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.carga_excel import cargar_archivos_a_bd

cargas_bp = Blueprint("cargas", __name__)


@cargas_bp.route("/cargar", methods=["GET", "POST"])
def cargar():
    """Formulario y procesamiento de subida de los archivos Excel."""
    if request.method == "POST":
        archivo_maestro = request.files.get("maestro")
        archivo_evaluaciones = request.files.get("evaluaciones")

        if not archivo_maestro or not archivo_evaluaciones or not archivo_maestro.filename or not archivo_evaluaciones.filename:
            flash("Debes seleccionar ambos archivos Excel para continuar.", "error")
            return render_template("cargar.html")

        try:
            total_est, total_eval = cargar_archivos_a_bd(archivo_maestro, archivo_evaluaciones)
            flash(
                f"Archivos cargados con éxito en la base de datos: {total_est} estudiantes y {total_eval} evaluaciones.",
                "success",
            )
            return redirect(url_for("tablero.index"))
        except Exception as e:
            flash(f"Error al procesar los archivos: {str(e)}", "error")
            return render_template("cargar.html")

    return render_template("cargar.html")
