# PLAN — App de Certificados (Academia Horizonte)

Objetivo: automatizar el cruce manual Excel/Word en una app web Flask con reglas fijas R1–R6.
Orden de construcción: primero cruce de datos, luego backend, al final interfaz.
No se avanza de etapa sin pasar su validación.

## Etapa 1 — Validar el cruce de datos (sin servidor)
- Qué haré:
  1. Lectura de `insumos/Maestro_Estudiantes.xlsx` (hoja `Estudiantes`) y `insumos/Registro_Evaluaciones.xlsx` (hoja `Evaluaciones`) con pandas + openpyxl.
  2. Normalizar `Identificacion` a texto con `strip()` en ambos archivos.
  3. Agrupar por `(identificacion, programa)`; Promedio = suma Notas / módulos cursados; Asistencia = promedio `Asistencia_Pct` (2 decimales).
  4. Clasificar con límites inclusivos (`>=`): Aprobación (≥70 y ≥80), Participación (<70 y ≥80), Sin certificado (<80). Detectar R6: sin evaluaciones, huérfana, asistencia <50.
- Cómo la validamos (puerta de salida):
  - `uv run python -m unittest tests.test_cifras_control -v` en verde: 19 Aprobación, 3 Participación, 1 Sin certificado, 3 inconsistencias (304560321, 999880777, Fernanda 36.25); Camila 91.25/96.25 y Luis 72.0/81.67 correctos; ZIP de 22.

## Etapa 2 — Backend con Flask + Supabase
- Qué haré:
  1. `models/datos.py`: conexión con `DATABASE_URL` (dotenv) y `prepare_threshold=None`; crear tablas; `insertar_*` (reemplazo total) y lecturas.
  2. `services/carga_excel.py`: validar columnas y cargar ambos Excel a la DB vía `cargar_datos.py`.
  3. `models/certificados.py`: función `procesar_reglas_negocio()` con fallback a Excel si la DB está vacía o falla.
  4. `services/generador_pdf.py`: PDF fpdf2 A4 horizontal por certificado.
  5. `controllers/` + `app.py`: rutas `/`, `/cargar`, `/certificado/<id>/<programa>`, `/descargar-todos` (solo orquestan, no calculan).
- Cómo la validamos:
  - `uv run cargar_datos.py` deja 24 estudiantes y 88 evaluaciones en Supabase.
  - Tablero con DB arriba y con DB apagada da las mismas cifras (prueba el fallback).
  - Descarga de 1 PDF válido (`%PDF`, >1000 bytes) y ZIP con 22 archivos.

## Etapa 3 — Interfaz (Salón, solo muestra)
- Qué haré:
  1. `views/` Jinja: tablero (contadores, tabla, alertas), formulario `/cargar`, botones de PDF y ZIP. Estilo azul marino `#14213D` y dorado `#B8923D`.
  2. Verificar que ninguna plantilla calcule: todo número ya viene del backend.
- Cómo la validamos:
  - Recorrido manual en `http://localhost:5000`: tablero muestra 19/3/1/3, alertas con los 3 casos, PDF de Camila y Luis correctos, ZIP descarga 22.
  - Revisión final: sin cambios en `insumos/`, sin secretos en código, `vercel.json` intacto.
