"""
tests/test_cifras_control.py - Suite integral de pruebas para validar todas las cifras de control de AGENTS.md.
Prueba: Tablero, Inconsistencias, PDF de Camila, PDF de Luis y el .ZIP masivo.
"""
import io
import zipfile
import unittest
from services.carga_excel import procesar_maestro, procesar_evaluaciones
from models.certificados import procesar_reglas_negocio
from services.generador_pdf import crear_pdf_certificado
from app import app


class TestCifrasControl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Cargar datos directamente desde los Excel de insumos
        cls.estudiantes = procesar_maestro("insumos/Maestro_Estudiantes.xlsx")
        cls.evaluaciones = procesar_evaluaciones("insumos/Registro_Evaluaciones.xlsx")
        cls.datos = procesar_reglas_negocio(cls.estudiantes, cls.evaluaciones)
        cls.client = app.test_client()

    def test_01_cifras_globales_control(self):
        """Verifica que salgan exactamente 19 Aprobación, 3 Participación, 1 Sin certificado y 3 Inconsistencias."""
        contadores = self.datos["contadores"]
        self.assertEqual(contadores["aprobacion"], 19, f"Esperado 19 Aprobación, obtenido: {contadores['aprobacion']}")
        self.assertEqual(contadores["participacion"], 3, f"Esperado 3 Participación, obtenido: {contadores['participacion']}")
        self.assertEqual(contadores["sin_certificado"], 1, f"Esperado 1 Sin certificado, obtenido: {contadores['sin_certificado']}")
        self.assertEqual(contadores["inconsistencias"], 3, f"Esperado 3 Inconsistencias, obtenido: {contadores['inconsistencias']}")

    def test_02_detalle_inconsistencias(self):
        """Verifica las 3 inconsistencias esperadas: Javier Espinoza, 999880777 y Fernanda Zúñiga."""
        inconsistencias = self.datos["inconsistencias"]
        ids_inconsistentes = [str(i["identificacion"]) for i in inconsistencias]

        self.assertIn("304560321", ids_inconsistentes, "Falta Javier Espinoza (sin evaluaciones)")
        self.assertIn("999880777", ids_inconsistentes, "Falta 999880777 (evaluación huérfana)")
        self.assertIn("111230984", ids_inconsistentes, "Falta Fernanda Zúñiga (asistencia < 50%)")

        # Verificar asistencia de Fernanda Zúñiga = 36.25%
        fernanda = next(e for e in self.datos["estudiantes"] if e["identificacion"] == "111230984")
        self.assertEqual(fernanda["asistencia"], 36.25, f"Asistencia de Fernanda debe ser 36.25, es {fernanda['asistencia']}")
        self.assertEqual(fernanda["estado"], "Sin certificado")

    def test_03_caso_control_camila_rojas(self):
        """Camila Rojas Méndez 101230456 = 91.25 / 96.25 Aprobación."""
        camila = next(e for e in self.datos["estudiantes"] if e["identificacion"] == "101230456")
        self.assertEqual(camila["promedio"], 91.25, f"Promedio Camila esperado 91.25, obtenido: {camila['promedio']}")
        self.assertEqual(camila["asistencia"], 96.25, f"Asistencia Camila esperada 96.25, obtenida: {camila['asistencia']}")
        self.assertEqual(camila["estado"], "Aprobación")
        self.assertTrue(camila["certificable"])

    def test_04_caso_control_luis_acuna(self):
        """Luis Acuña Blanco 402340178 = 72.0 / 81.67 Aprobación."""
        luis = next(e for e in self.datos["estudiantes"] if e["identificacion"] == "402340178")
        self.assertEqual(luis["promedio"], 72.0, f"Promedio Luis esperado 72.0, obtenido: {luis['promedio']}")
        self.assertEqual(luis["asistencia"], 81.67, f"Asistencia Luis esperada 81.67, obtenida: {luis['asistencia']}")
        self.assertEqual(luis["estado"], "Aprobación")
        self.assertTrue(luis["certificable"])

    def test_05_generacion_pdf_camila(self):
        """Verifica la generación del PDF de Camila Rojas."""
        camila = next(e for e in self.datos["estudiantes"] if e["identificacion"] == "101230456")
        pdf_bytes = crear_pdf_certificado(camila)
        self.assertTrue(len(pdf_bytes) > 1000, "El PDF de Camila está vacío o es muy pequeño")
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "El archivo generado no es un PDF válido")

    def test_06_generacion_pdf_luis(self):
        """Verifica la generación del PDF de Luis Acuña."""
        luis = next(e for e in self.datos["estudiantes"] if e["identificacion"] == "402340178")
        pdf_bytes = crear_pdf_certificado(luis)
        self.assertTrue(len(pdf_bytes) > 1000, "El PDF de Luis está vacío o es muy pequeño")
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "El archivo generado no es un PDF válido")

    def test_07_emision_zip_22_archivos(self):
        """Verifica que el .ZIP contenga exactamente 22 certificados (19 Aprobación + 3 Participación)."""
        certificables = [e for e in self.datos["estudiantes"] if e.get("certificable", False)]
        self.assertEqual(len(certificables), 22, f"Esperados 22 certificados emitibles, encontrados: {len(certificables)}")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for est in certificables:
                pdf_bytes = crear_pdf_certificado(est)
                zf.writestr(f"Certificado_{est['identificacion']}.pdf", pdf_bytes)

        zip_buffer.seek(0)
        with zipfile.ZipFile(zip_buffer, mode="r") as zf:
            archivos = zf.namelist()
            self.assertEqual(len(archivos), 22, f"El ZIP debe contener exactamente 22 archivos, tiene: {len(archivos)}")

    def test_08_no_emision_inconsistencias_o_sin_certificado(self):
        """Verifica que Javier Espinoza y Fernanda Zúñiga NO sean certificables."""
        javier = next(e for e in self.datos["estudiantes"] if e["identificacion"] == "304560321")
        fernanda = next(e for e in self.datos["estudiantes"] if e["identificacion"] == "111230984")
        self.assertFalse(javier.get("certificable", False), "Javier Espinoza no debe ser certificable")
        self.assertFalse(fernanda.get("certificable", False), "Fernanda Zúñiga no debe ser certificable")


if __name__ == "__main__":
    unittest.main()
