"""
cargar_datos.py - Script ejecutable para inicializar las tablas en Supabase y cargar los datos desde los Excel.
"""
from models.datos import crear_tablas, contar_estudiantes, contar_evaluaciones
from services.carga_excel import cargar_archivos_a_bd


def main():
    print("=== Conectando a Supabase y asegurando tablas ===")
    crear_tablas()
    print("Tablas 'estudiantes' y 'evaluaciones' verificadas/creadas con éxito.")
    
    print("\n=== Procesando archivos Excel y cargando datos ===")
    total_est, total_eval = cargar_archivos_a_bd()
    print(f"Procesados desde Excel: {total_est} estudiantes y {total_eval} evaluaciones.")
    
    print("\n=== Verificando registros en la base de datos ===")
    est_en_bd = contar_estudiantes()
    eval_en_bd = contar_evaluaciones()
    
    print(f"Filas en tabla 'estudiantes': {est_en_bd}")
    print(f"Filas en tabla 'evaluaciones': {eval_en_bd}")
    print("\n¡Carga completada con éxito!")


if __name__ == "__main__":
    main()
