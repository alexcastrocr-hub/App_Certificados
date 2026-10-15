"""
services/carga_excel.py - Lógica de lectura y validación de los archivos Excel y guardado en Supabase.
"""
import pandas as pd
from pathlib import Path
from models.datos import insertar_estudiantes, insertar_evaluaciones

# Rutas absolutas ancladas a la ubicación de este archivo:
# funcionan sin importar desde qué carpeta se ejecute la app.
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_MAESTRO = BASE_DIR / "insumos" / "Maestro_Estudiantes.xlsx"
RUTA_EVALUACIONES = BASE_DIR / "insumos" / "Registro_Evaluaciones.xlsx"

COLUMNAS_MAESTRO = ["Identificacion", "Nombre_Completo", "Correo", "Programa", "Cohorte"]
COLUMNAS_EVALUACIONES = ["Identificacion", "Programa", "Modulo", "Nota", "Asistencia_Pct", "Fecha_Cierre"]


def procesar_maestro(ruta_o_archivo=RUTA_MAESTRO) -> list[dict]:
    """Lee y valida el archivo Maestro_Estudiantes.xlsx."""
    df = pd.read_excel(ruta_o_archivo, sheet_name="Estudiantes", dtype=str)
    
    # Validar columnas presentes
    columnas_faltantes = [col for col in COLUMNAS_MAESTRO if col not in df.columns]
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas en Maestro_Estudiantes.xlsx: {columnas_faltantes}")
    
    estudiantes = []
    for _, fila in df.iterrows():
        identificacion = str(fila["Identificacion"]).strip()
        nombre = str(fila["Nombre_Completo"]).strip()
        correo = str(fila["Correo"]).strip() if pd.notna(fila["Correo"]) else None
        programa = str(fila["Programa"]).strip()
        cohorte = str(fila["Cohorte"]).strip() if pd.notna(fila["Cohorte"]) else None
        
        if identificacion and identificacion.lower() != "nan":
            estudiantes.append({
                "identificacion": identificacion,
                "nombre_completo": nombre,
                "correo": correo,
                "programa": programa,
                "cohorte": cohorte,
            })
            
    return estudiantes


def procesar_evaluaciones(ruta_o_archivo=RUTA_EVALUACIONES) -> list[dict]:
    """Lee y valida el archivo Registro_Evaluaciones.xlsx."""
    df = pd.read_excel(ruta_o_archivo, sheet_name="Evaluaciones")
    
    columnas_faltantes = [col for col in COLUMNAS_EVALUACIONES if col not in df.columns]
    if columnas_faltantes:
        raise ValueError(f"Faltan columnas en Registro_Evaluaciones.xlsx: {columnas_faltantes}")
    
    evaluaciones = []
    for _, fila in df.iterrows():
        identificacion = str(fila["Identificacion"]).strip()
        programa = str(fila["Programa"]).strip()
        modulo = str(fila["Modulo"]).strip()
        nota = float(fila["Nota"]) if pd.notna(fila["Nota"]) else 0.0
        asistencia = float(fila["Asistencia_Pct"]) if pd.notna(fila["Asistencia_Pct"]) else 0.0
        
        fecha_cierre = None
        if pd.notna(fila["Fecha_Cierre"]):
            fecha_val = pd.to_datetime(fila["Fecha_Cierre"])
            fecha_cierre = fecha_val.strftime("%Y-%m-%d")
            
        if identificacion and identificacion.lower() != "nan":
            evaluaciones.append({
                "identificacion": identificacion,
                "programa": programa,
                "modulo": modulo,
                "nota": round(nota, 2),
                "asistencia_pct": round(asistencia, 2),
                "fecha_cierre": fecha_cierre,
            })
            
    return evaluaciones


def cargar_archivos_a_bd(ruta_maestro=RUTA_MAESTRO, ruta_evaluaciones=RUTA_EVALUACIONES):
    """Lee ambos Excel y los guarda en Supabase reemplazando los datos previos."""
    estudiantes = procesar_maestro(ruta_maestro)
    evaluaciones = procesar_evaluaciones(ruta_evaluaciones)
    
    insertar_estudiantes(estudiantes)
    insertar_evaluaciones(evaluaciones)
    
    return len(estudiantes), len(evaluaciones)
