"""
models/certificados.py - Reglas de negocio puras para la emisión de certificados de la Academia.
Constantes obligatorias: NOTA_MINIMA = 70, ASISTENCIA_MINIMA = 80.
Reglas: R1 a R6.
"""
from models.datos import obtener_estudiantes, obtener_evaluaciones
from services.carga_excel import procesar_maestro, procesar_evaluaciones

# Constantes requeridas por AGENTS.md
NOTA_MINIMA = 70.0
ASISTENCIA_MINIMA = 80.0
ASISTENCIA_CRITICA_INCONSISTENCIA = 50.0


def calcular_promedio(valores):
    # FUNCION: recibe una lista de numeros y devuelve su promedio redondeado a 2 decimales.
    # VARIABLES: total (numero, suma de las notas) y n (entero, modulos cursados).
    # TIPOS: entra lista de numeros, sale un numero (o None si no hay datos).
    # CONDICIONAL: si la lista esta vacia no se puede dividir, se devuelve None.
    if len(valores) == 0:  # CONDICIONAL: caso borde sin modulos
        return None
    total = sum(valores)  # VARIABLE de tipo numero: suma de las notas
    n = len(valores)  # VARIABLE de tipo entero: cantidad de modulos cursados
    return round(total / n, 2)


def decidir_certificado(promedio, asistencia):
    # FUNCION: decide el tipo de certificado con CONDICIONALES encadenados.
    # TIPOS: promedio y asistencia son numeros (o None); devuelve un texto.
    if promedio is None or asistencia is None:  # CONDICIONAL: sin datos -> inconsistencia
        return "Inconsistencia"
    if promedio >= NOTA_MINIMA and asistencia >= ASISTENCIA_MINIMA:  # CONDICIONAL: Aprobacion (limites INCLUYEN el valor)
        return "Aprobación"
    if promedio < NOTA_MINIMA and asistencia >= ASISTENCIA_MINIMA:  # CONDICIONAL: Participacion
        return "Participación"
    return "Sin certificado"  # CONDICIONAL final: asistencia < 80


def procesar_reglas_negocio(estudiantes=None, evaluaciones=None) -> dict:
    """
    Aplica las reglas R1 a R6 sobre los datos de estudiantes y evaluaciones.
    Si no se proporcionan listas, intenta consultar desde Supabase vía models.datos.
    Si la base de datos aún no está disponible o no tiene datos, usa de respaldo los Excel de insumos/.
    """
    if estudiantes is None:
        try:
            estudiantes = obtener_estudiantes()
            if not estudiantes:
                estudiantes = procesar_maestro()
        except Exception:
            estudiantes = procesar_maestro()

    if evaluaciones is None:
        try:
            evaluaciones = obtener_evaluaciones()
            if not evaluaciones:
                evaluaciones = procesar_evaluaciones()
        except Exception:
            evaluaciones = procesar_evaluaciones()

    # R1: Agrupar evaluaciones por (identificacion, programa)
    evals_por_clave = {}
    for ev in evaluaciones:
        ident = str(ev["identificacion"]).strip()
        prog = str(ev["programa"]).strip()
        clave = (ident, prog)
        if clave not in evals_por_clave:
            evals_por_clave[clave] = []
        evals_por_clave[clave].append(ev)

    # Diccionario de estudiantes por clave para búsqueda rápida
    estudiantes_por_clave = {}
    for est in estudiantes:
        ident = str(est["identificacion"]).strip()
        prog = str(est["programa"]).strip()
        estudiantes_por_clave[(ident, prog)] = est

    lista_estudiantes = []
    inconsistencias = []
    contadores = {
        "aprobacion": 0,
        "participacion": 0,
        "sin_certificado": 0,
        "inconsistencias": 0,
    }

    # BUCLE: recorro cada estudiante del maestro una vez
    for est in estudiantes:
        ident = str(est["identificacion"]).strip()
        prog = str(est["programa"]).strip()
        nombre = est["nombre_completo"]
        clave = (ident, prog)

        # CONDICIONAL: pregunto si esa clave (identificacion + programa) tiene evaluaciones
        if clave not in evals_por_clave:
            # R6: Estudiante del maestro sin evaluaciones
            inconsistencias.append({
                "identificacion": ident,
                "nombre": nombre,
                "programa": prog,
                "tipo": "Estudiante sin evaluaciones",
                "detalle": "Está registrado en el maestro pero no cuenta con módulos evaluados.",
            })
            lista_estudiantes.append({
                "identificacion": ident,
                "nombre": nombre,
                "programa": prog,
                "correo": est.get("correo"),
                "modulos": 0,  # VARIABLE de tipo entero: modulos cursados
                "promedio": None,
                "asistencia": None,
                "estado": "Inconsistencia",
                "certificable": False,
            })
        else:
            grupo_evals = evals_por_clave[clave]
            # R2: Promedio = suma de Notas / modulos; Asistencia = promedio de asistencia_pct
            notas = [float(e["nota"]) for e in grupo_evals]  # VARIABLE de tipo lista
            asistencias = [float(e["asistencia_pct"]) for e in grupo_evals]  # VARIABLE de tipo lista
            promedio_nota = calcular_promedio(notas)  # FUNCION: reutiliza la logica validada
            promedio_asist = calcular_promedio(asistencias)  # FUNCION: misma funcion para asistencia
            modulos = len(grupo_evals)  # VARIABLE de tipo entero: modulos cursados

            estado = ""  # VARIABLE de tipo texto: resultado de la decision
            certificable = False  # VARIABLE de tipo booleano: si se puede emitir PDF

            # R6: Asistencia menor al 50% (alerta e inconsistencia)
            if promedio_asist < ASISTENCIA_CRITICA_INCONSISTENCIA:
                inconsistencias.append({
                    "identificacion": ident,
                    "nombre": nombre,
                    "programa": prog,
                    "tipo": "Asistencia crítica (< 50%)",
                    "detalle": f"Promedio {promedio_nota} con asistencia de {promedio_asist}% (posible deserción).",
                })

            # Clasificación con la FUNCION decidir_certificado (CONDICIONALES adentro)
            estado = decidir_certificado(promedio_nota, promedio_asist)
            # CONDICIONAL: solo Aprobacion y Participacion se pueden certificar
            if estado in ("Aprobación", "Participación"):
                certificable = True
            # CONDICIONAL: cuento cada caso para los contadores de arriba
            if estado == "Aprobación":
                contadores["aprobacion"] += 1
            elif estado == "Participación":
                contadores["participacion"] += 1
            else:
                # R5: Sin certificado (asistencia < 80)
                contadores["sin_certificado"] += 1

            lista_estudiantes.append({
                "identificacion": ident,
                "nombre": nombre,
                "programa": prog,
                "correo": est.get("correo"),
                "modulos": modulos,
                "promedio": promedio_nota,
                "asistencia": promedio_asist,
                "estado": estado,
                "certificable": certificable,
            })

    # R6: Evaluaciones con identificación que no está en el maestro (huérfanos)
    # BUCLE: reviso cada par evaluado y pregunto con un CONDICIONAL si existe en el maestro
    for clave, evals in evals_por_clave.items():
        if clave not in estudiantes_por_clave:  # CONDICIONAL: no esta en el maestro -> huerfana
            ident, prog = clave
            notas = [float(e["nota"]) for e in evals]
            asistencias = [float(e["asistencia_pct"]) for e in evals]
            prom_n = calcular_promedio(notas)  # FUNCION reutilizada
            prom_a = calcular_promedio(asistencias)  # FUNCION reutilizada
            inconsistencias.append({
                "identificacion": ident,
                "nombre": "(No registrado en Maestro)",
                "programa": prog,
                "tipo": "Evaluación huérfana",
                "detalle": f"Tiene registros de notas (Promedio: {prom_n}, Asist: {prom_a}%) pero no existe en el archivo maestro.",
            })

    contadores["inconsistencias"] = len(inconsistencias)

    # Ordeno la tabla por programa y nombre para mostrarla siempre igual
    lista_estudiantes = sorted(lista_estudiantes, key=lambda e: (e["programa"], e["nombre"]))

    return {
        "contadores": contadores,
        "estudiantes": lista_estudiantes,
        "inconsistencias": inconsistencias,
    }
