"""
controllers/certificados.py - Controlador para la generación de PDFs y descarga masiva en ZIP.
Rutas: /certificado/<identificacion>/<programa> y /descargar-todos.
No emite certificados para 'Sin certificado' ni inconsistencias.
"""
import io
import zipfile
from flask import Blueprint, send_file, abort, Response
from models.certificados import procesar_reglas_negocio
from services.generador_pdf import crear_pdf_certificado

certificados_bp = Blueprint("certificados", __name__)


@certificados_bp.route("/certificado/<identificacion>/<programa>")
def descargar_certificado_individual(identificacion: str, programa: str):
    """Genera y descarga el PDF del certificado para un estudiante específico."""
    ident_limpia = str(identificacion).strip()
    prog_limpio = str(programa).strip()

    datos = procesar_reglas_negocio()
    estudiante = None
    for est in datos["estudiantes"]:
        if est["identificacion"] == ident_limpia and est["programa"] == prog_limpio:
            estudiante = est
            break

    if not estudiante:
        return Response("Estudiante o programa no encontrado.", status=404, mimetype="text/plain; charset=utf-8")

    if not estudiante.get("certificable", False):
        return Response(
            f"No se genera certificado: el estado del estudiante es '{estudiante.get('estado')}'.",
            status=400,
            mimetype="text/plain; charset=utf-8",
        )

    pdf_bytes = crear_pdf_certificado(estudiante)
    nombre_archivo = f"Certificado_{ident_limpia}_{prog_limpio.replace(' ', '_')}.pdf"

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=nombre_archivo,
    )


@certificados_bp.route("/descargar-todos")
def descargar_todos_los_certificados():
    """Genera un archivo .ZIP con todos los certificados emitibles (Aprobación y Participación)."""
    datos = procesar_reglas_negocio()
    estudiantes_certificables = [e for e in datos["estudiantes"] if e.get("certificable", False)]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for est in estudiantes_certificables:
            pdf_bytes = crear_pdf_certificado(est)
            nombre_archivo = f"Certificado_{est['identificacion']}_{est['programa'].replace(' ', '_')}.pdf"
            zf.writestr(nombre_archivo, pdf_bytes)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="certificados_academia.zip",
    )
