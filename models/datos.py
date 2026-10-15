"""
models/datos.py - Único archivo autorizado para comunicarse con Supabase (PostgreSQL).
Lee DATABASE_URL desde .env usando python-dotenv y psycopg con prepare_threshold=None.
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Cargar variables del entorno
load_dotenv()


def get_connection():
    """Obtiene una conexión a Supabase con prepare_threshold=None."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url or not database_url.strip():
        raise ValueError("DATABASE_URL no está configurada o está vacía en el archivo .env")
    return psycopg.connect(database_url, prepare_threshold=None, row_factory=dict_row)


def crear_tablas():
    """Crea las tablas estudiantes y evaluaciones si no existen."""
    sql_estudiantes = """
    CREATE TABLE IF NOT EXISTS estudiantes (
        identificacion TEXT PRIMARY KEY,
        nombre_completo TEXT NOT NULL,
        correo TEXT,
        programa TEXT NOT NULL,
        cohorte TEXT
    );
    """
    sql_evaluaciones = """
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id SERIAL PRIMARY KEY,
        identificacion TEXT NOT NULL,
        programa TEXT NOT NULL,
        modulo TEXT NOT NULL,
        nota NUMERIC(5,2) NOT NULL,
        asistencia_pct NUMERIC(5,2) NOT NULL,
        fecha_cierre DATE
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_estudiantes)
            cur.execute(sql_evaluaciones)
        conn.commit()


def insertar_estudiantes(estudiantes: list[dict]):
    """Reemplaza los datos en la tabla estudiantes."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM estudiantes;")
            for est in estudiantes:
                cur.execute(
                    """
                    INSERT INTO estudiantes (identificacion, nombre_completo, correo, programa, cohorte)
                    VALUES (%(identificacion)s, %(nombre_completo)s, %(correo)s, %(programa)s, %(cohorte)s);
                    """,
                    est,
                )
        conn.commit()


def insertar_evaluaciones(evaluaciones: list[dict]):
    """Reemplaza los datos en la tabla evaluaciones."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM evaluaciones;")
            for ev in evaluaciones:
                cur.execute(
                    """
                    INSERT INTO evaluaciones (identificacion, programa, modulo, nota, asistencia_pct, fecha_cierre)
                    VALUES (%(identificacion)s, %(programa)s, %(modulo)s, %(nota)s, %(asistencia_pct)s, %(fecha_cierre)s);
                    """,
                    ev,
                )
        conn.commit()


def contar_estudiantes() -> int:
    """Retorna la cantidad de registros en la tabla estudiantes."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM estudiantes;")
            row = cur.fetchone()
            return row["total"] if row else 0


def contar_evaluaciones() -> int:
    """Retorna la cantidad de registros en la tabla evaluaciones."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM evaluaciones;")
            row = cur.fetchone()
            return row["total"] if row else 0


def obtener_estudiantes() -> list[dict]:
    """Retorna la lista de todos los estudiantes."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT identificacion, nombre_completo, correo, programa, cohorte FROM estudiantes ORDER BY nombre_completo ASC;"
            )
            return cur.fetchall()


def obtener_evaluaciones() -> list[dict]:
    """Retorna la lista de todas las evaluaciones."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, identificacion, programa, modulo, nota, asistencia_pct, fecha_cierre FROM evaluaciones ORDER BY identificacion, modulo;"
            )
            return cur.fetchall()
