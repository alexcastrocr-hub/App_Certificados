"""
services/generador_pdf.py - Generación de certificados en PDF con fpdf2 en orientación A4 horizontal.
Colores institucionales: Azul Marino (#14213D) y Dorado (#B8923D).
"""
import io
from fpdf import FPDF


class CertificadoPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)

    def dibujar_marco(self):
        """Dibuja un marco ornamental elegante con los colores institucionales."""
        # Fondo blanco
        self.set_fill_color(255, 255, 255)
        self.rect(0, 0, 297, 210, "F")

        # Borde exterior Azul Marino (#14213D -> R:20, G:33, B:61)
        self.set_line_width(4)
        self.set_draw_color(20, 33, 61)
        self.rect(8, 8, 281, 194)

        # Borde interior Dorado (#B8923D -> R:184, G:146, B:61)
        self.set_line_width(1.5)
        self.set_draw_color(184, 146, 61)
        self.rect(12, 12, 273, 186)

        # Detalles en las esquinas
        self.set_fill_color(184, 146, 61)
        tam = 6
        self.rect(12, 12, tam, tam, "F")
        self.rect(285 - tam, 12, tam, tam, "F")
        self.rect(12, 198 - tam, tam, tam, "F")
        self.rect(285 - tam, 198 - tam, tam, tam, "F")


def crear_pdf_certificado(estudiante: dict) -> bytes:
    """
    Genera el certificado en PDF para un estudiante dado.
    estudiante debe ser un diccionario con:
    nombre, identificacion, programa, cohorte, promedio, asistencia, estado
    """
    pdf = CertificadoPDF()
    pdf.add_page()
    pdf.dibujar_marco()

    # Encabezado institucional
    pdf.set_y(22)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(184, 146, 61)  # Dorado
    pdf.cell(0, 8, "ACADEMIA DE FORMACIÓN PROFESIONAL Y NEGOCIOS", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(0, 5, "DIVISIÓN DE CERTIFICACIÓN ACADÉMICA", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # Título del Certificado según el tipo
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(20, 33, 61)  # Azul Marino
    tipo_cert = "Certificado de Aprobación" if estudiante.get("estado") == "Aprobación" else "Certificado de Participación"
    pdf.cell(0, 12, tipo_cert.upper(), align="C", new_x="LMARGIN", new_y="NEXT")

    # Línea decorativa dorada
    pdf.set_draw_color(184, 146, 61)
    pdf.set_line_width(1)
    pdf.line(90, pdf.get_y(), 207, pdf.get_y())
    pdf.ln(8)

    # Texto de concesión
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(70, 80, 95)
    pdf.cell(0, 7, "Otorga el presente reconocimiento a:", align="C", new_x="LMARGIN", new_y="NEXT")

    # Nombre del Estudiante
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 33, 61)
    nombre = estudiante.get("nombre", "Estudiante")
    pdf.cell(0, 11, nombre, align="C", new_x="LMARGIN", new_y="NEXT")

    # Identificación
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 110, 120)
    ident = estudiante.get("identificacion", "")
    pdf.cell(0, 6, f"Identificación: {ident}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # Programa y Cohorte
    programa = estudiante.get("programa", "Programa")
    cohorte = estudiante.get("cohorte", "2026")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(50, 60, 75)
    texto_cumplimiento = (
        f"Por haber completado y aprobado satisfactoriamente los requisitos del programa formativo:"
        if estudiante.get("estado") == "Aprobación"
        else f"Por su activa asistencia y participación en las sesiones del programa formativo:"
    )
    pdf.cell(0, 6, texto_cumplimiento, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(184, 146, 61)  # Dorado
    pdf.cell(0, 9, f"{programa}", align="C", new_x="LMARGIN", new_y="NEXT")

    if cohorte:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 110, 120)
        pdf.cell(0, 5, f"Cohorte: {cohorte}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)

    # Métricas de Desempeño
    promedio = estudiante.get("promedio")
    asistencia = estudiante.get("asistencia")
    prom_str = f"{promedio:.2f}" if promedio is not None else "-"
    asist_str = f"{asistencia:.2f}%" if asistencia is not None else "-"

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(40, 50, 65)
    pdf.cell(0, 6, f"Promedio Final: {prom_str}  |  Asistencia Registrada: {asist_str}", align="C", new_x="LMARGIN", new_y="NEXT")

    # Firmas y pie de página
    pdf.set_y(168)
    linea_y = 175

    # Firma 1: Dirección Académica
    pdf.set_draw_color(150, 160, 170)
    pdf.set_line_width(0.5)
    pdf.line(45, linea_y, 115, linea_y)
    pdf.set_xy(45, linea_y + 2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 33, 61)
    pdf.cell(70, 5, "Dirección Académica", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(45, linea_y + 7)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(120, 130, 140)
    pdf.cell(70, 4, "Academia de Formación", align="C", new_x="LMARGIN", new_y="NEXT")

    # Firma 2: Coordinación del Programa
    pdf.line(182, linea_y, 252, linea_y)
    pdf.set_xy(182, linea_y + 2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 33, 61)
    pdf.cell(70, 5, "Coordinación de Programa", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_xy(182, linea_y + 7)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(120, 130, 140)
    pdf.cell(70, 4, "Registro y Certificaciones", align="C", new_x="LMARGIN", new_y="NEXT")

    # Generar bytes en memoria
    return bytes(pdf.output())
