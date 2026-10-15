# App de Certificados de la Academia

Sistema web para el procesamiento de evaluaciones y emisión de certificados en PDF de la Academia de Formación Técnica y Negocios.

## Tecnologías
- Python 3.12 gestionado con [uv](https://github.com/astral-sh/uv)
- Flask
- Supabase (PostgreSQL) con `psycopg`
- Generación de PDF con `fpdf2`

## Arquitectura (MVC)
- `models/datos.py`: Conexión y persistencia con Supabase.
- `models/certificados.py`: Reglas del negocio (R1 a R6) y constantes.
- `services/carga_excel.py`: Lectura y procesamiento de archivos Excel.
- `services/generador_pdf.py`: Generación de certificados en PDF A4 horizontal.
- `controllers/`: Rutas y orquestación de la aplicación Flask.
- `views/`: Plantillas Jinja con diseño institucional (#14213D y #B8923D).
- `app.py`: Servidor web Flask.

## Instrucciones de Ejecución
1. Instalar dependencias con `uv`:
   ```bash
   uv sync
   ```
2. Cargar datos iniciales en Supabase:
   ```bash
   uv run cargar_datos.py
   ```
3. Iniciar la aplicación web:
   ```bash
   uv run python app.py
   ```
   Abrir en el navegador: `http://localhost:5000`
