# App de Certificados — Academia Horizonte

Academia Horizonte (formación técnica a empresas): automatizar emisión de certificados por cohorte, hoy manual en Excel/Word. App web Flask sin IA, solo reglas fijas R1-R6.

## Comandos (usar `uv`, nunca `pip`)
- `uv sync` — instalar dependencias (Python >=3.12,<3.13).
- `uv run cargar_datos.py` — crear tablas y cargar `insumos/` a Supabase.
- `uv run python app.py` — servidor local en `http://localhost:5000`.
- `uv run python -m unittest tests.test_cifras_control -v` — verificación principal (lee Excel directo, no necesita DB).

## Arquitectura MVC (respetarla: Bodega → Cocina → Salón)
- Decisión técnica: Excel con **pandas + openpyxl** (agrupado y promedios con `groupby`); web con **Flask + Jinja** (simple, 4 rutas, despliegue Vercel); PDF con **fpdf2**; DB con **psycopg + python-dotenv**. Descartados: `xlrd` (no lee `.xlsx` nuevos), Django (exceso), FastAPI (orientado a API, no a HTML).
- Bodega = `insumos/` (datos, no se tocan). Cocina = backend Python/Flask (`app.py`, `models/`, `services/`, `controllers/`): toda la lógica va aquí, NUNCA en la interfaz. Salón = `views/` HTML/Jinja: solo muestra, no calcula ni decide.
- `models/datos.py`: único que habla con Supabase. `models/certificados.py`: reglas R1-R6 (`NOTA_MINIMA=70`, `ASISTENCIA_MINIMA=80`).
- `services/carga_excel.py`: lee Excel y guarda en DB. `services/generador_pdf.py`: PDF fpdf2 A4 horizontal.
- `controllers/`: solo rutas/orquestación, no calculan (`tablero.py`, `cargas.py`, `certificados.py`). `views/`: solo Jinja, colores `#14213D` / `#B8923D`.
- `app.py` expone variable `app`, `template_folder="views"`, registra 3 blueprints. Rutas: `/`, `/cargar`, `/certificado/<identificacion>/<programa>`, `/descargar-todos`. `vercel.json` reutiliza `app.py`.

## Datos y reglas no obvias
- `insumos/`: solo lectura, nunca modificar. Hojas `Estudiantes` (24 filas) y `Evaluaciones` (88 filas). `Identificacion` siempre texto con `strip()`.
- Un certificado por `(identificacion, programa)`. Promedio = suma Notas / módulos cursados; Asistencia = promedio `Asistencia_Pct` (2 decimales). Aprobación: Promedio >= 70 y Asistencia >= 80; Participación: Promedio < 70 y Asistencia >= 80; Sin certificado: Asistencia < 80. Límites INCLUYEN el valor.
- `procesar_reglas_negocio()` tiene fallback: si Supabase está vacía o falla, lee los Excel directo. No asumir que el tablero viene de la DB.
- DB: `DATABASE_URL` de `.env` vía `python-dotenv`; conexión psycopg exige `prepare_threshold=None` (pooler Supabase). Esquema: `estudiantes(identificacion TEXT PK)` y `evaluaciones(id SERIAL PK)`. `insertar_*` hace `DELETE` total antes de insertar.
- Cifras de aceptación: 19 Aprobación, 3 Participación, 1 Sin certificado, 3 inconsistencias (304560321 sin evaluaciones, 999880777 huérfana, Fernanda 111230984 asistencia 36.25). Controles: Camila 101230456 = 91.25/96.25 Aprobación; Luis 402340178 = 72.0/81.67 Aprobación. ZIP = 22 PDF.

## Restricciones y estilo
- Código simple y comentado en español, señalando los ladrillos: variables, tipos, condicionales, bucles y funciones.
- Nunca leer ni mostrar `.env`; nunca escribir contraseñas en código (ver `.env.ejemplo`, `.gitignore` ya ignora `.env`). `SECRET_KEY` se lee de entorno o se genera.
- Responder en español sencillo. Cambios por entregas pequeñas indicando capa y archivos.
