from app.db import getConnection
from datetime import datetime, timedelta
from typing import Dict, Any

def getTiempoEsperaPromedio() -> Dict[str, Any]:
    """
    Calcula el tiempo de espera promedio (Te)
    Fórmula: ∑(Hora_Atención - Hora_Cita) / Total_Atenciones
    Meta: <15 minutos
    """
    conn = getConnection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT
            AVG(
                EXTRACT(EPOCH FROM (
                    COALESCE(ra.hora_inicio, c.hora_atencion) - COALESCE(ra.hora_llegada, c.hora_cita)
                )) / 60
            ) as tiempo_promedio_minutos,
            COUNT(*) as total_atenciones
        FROM citas c
        LEFT JOIN registro_atencion ra ON ra.cita_id = c.id
        WHERE COALESCE(ra.hora_inicio, c.hora_atencion) IS NOT NULL
        AND COALESCE(ra.hora_llegada, c.hora_cita) IS NOT NULL
        AND c.estado = 'atendida'
    """)
    
    row = cur.fetchone()
    conn.close()
    
    tiempo_promedio = float(row[0]) if row[0] else 0.0
    total_atenciones = int(row[1]) if row[1] else 0
    
    return {
        "valor": round(tiempo_promedio, 2),
        "total_atenciones": total_atenciones,
        "meta": 15,
        "cumple_meta": tiempo_promedio < 15 if tiempo_promedio > 0 else None,
        "unidad": "minutos"
    }

def getTasaAusentismo() -> Dict[str, Any]:
    """
    Calcula la tasa de ausentismo (No-Show)
    Fórmula: (Citas_Incumplidas / Total_Citas_Reservadas) * 100
    Meta: Reducir del 30% al <10%
    """
    conn = getConnection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE estado IN ('cancelada', 'no_asistio')) as citas_incumplidas,
            COUNT(*) as total_citas
        FROM citas
        WHERE estado IN ('reservada', 'cancelada', 'no_asistio')
    """)
    
    row = cur.fetchone()
    conn.close()
    
    citas_incumplidas = int(row[0]) if row[0] else 0
    total_citas = int(row[1]) if row[1] else 0
    
    tasa = (citas_incumplidas / total_citas * 100) if total_citas > 0 else 0
    
    return {
        "valor": round(tasa, 2),
        "citas_incumplidas": citas_incumplidas,
        "total_citas": total_citas,
        "meta": 10,
        "cumple_meta": tasa < 10 if total_citas > 0 else None,
        "unidad": "porcentaje"
    }

def getTasaOcupacionMedica() -> Dict[str, Any]:
    """
    Calcula la tasa de ocupación médica
    Fórmula: (Horas_Atendidas / Horas_Programadas) * 100
    Meta: >85%
    """
    conn = getConnection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT
            DATE_TRUNC('week', CURRENT_DATE)::date as semana_inicio,
            (DATE_TRUNC('week', CURRENT_DATE)::date + INTERVAL '6 days')::date as semana_fin
    """)
    semana_inicio, semana_fin = cur.fetchone()

    # Cupos ofertados semanales basados en horario_medico.
    # Cada regla del medico se expande a los dias reales de la semana actual.
    # La duracion del turno sale de la disponibilidad activa de su especialidad.
    cur.execute("""
        SELECT 
            COALESCE(SUM(
                FLOOR(
                    EXTRACT(EPOCH FROM (hm.hora_fin - hm.hora_inicio)) / 60
                    / NULLIF(COALESCE(de.duracion_turno, 30), 0)
                )
            ), 0) as cupos_ofertados
        FROM horario_medico hm
        JOIN medicos m ON m.id = hm.medico_id
        JOIN LATERAL generate_series(
            GREATEST(hm.fecha_inicio, %s::date),
            LEAST(hm.fecha_fin, %s::date),
            interval '1 day'
        ) AS dias(fecha) ON true
        JOIN disponibilidad_especialidad de
          ON de.especialidad_id = m.especialidad_id
         AND dias.fecha::date BETWEEN de.fecha_inicio AND de.fecha_fin
         AND EXTRACT(ISODOW FROM dias.fecha)::int = de.dia_semana
         AND de.disponibilidad = true
        WHERE hm.fecha_inicio <= %s::date
          AND hm.fecha_fin >= %s::date
          AND EXTRACT(ISODOW FROM dias.fecha)::int = hm.dia_semana
    """, (semana_inicio, semana_fin, semana_fin, semana_inicio))
    
    cupos_ofertados_row = cur.fetchone()
    cupos_ofertados = int(cupos_ofertados_row[0]) if cupos_ofertados_row[0] else 0
    
    # Citas atendidas de la misma semana.
    cur.execute("""
        SELECT 
            COUNT(c.id) as citas_atendidas
        FROM citas c
        WHERE c.estado = 'atendida'
          AND c.fecha BETWEEN %s::date AND %s::date
    """, (semana_inicio, semana_fin))
    
    citas_atendidas_row = cur.fetchone()
    citas_atendidas = int(citas_atendidas_row[0]) if citas_atendidas_row[0] else 0
    
    conn.close()
    
    tasa = (citas_atendidas / cupos_ofertados * 100) if cupos_ofertados > 0 else 0
    
    return {
        "valor": round(tasa, 2),
        "citas_atendidas": citas_atendidas,
        "cupos_ofertados": cupos_ofertados,
        "semana_inicio": semana_inicio.isoformat(),
        "semana_fin": semana_fin.isoformat(),
        "meta": 85,
        "cumple_meta": tasa > 85 if cupos_ofertados > 0 else None,
        "unidad": "porcentaje"
    }

def getNivelSatisfaccion() -> Dict[str, Any]:
    """
    Calcula el nivel de satisfacción del usuario
    Fórmula: Promedio de calificación (Escala 1-5) post-atención
    Meta: >4.0/5.0
    """
    conn = getConnection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            AVG(calificacion) as promedio_calificacion,
            COUNT(*) as total_calificaciones
        FROM calificaciones
    """)
    
    row = cur.fetchone()
    conn.close()
    
    promedio = float(row[0]) if row[0] else 0.0
    total_calificaciones = int(row[1]) if row[1] else 0
    
    return {
        "valor": round(promedio, 2),
        "total_calificaciones": total_calificaciones,
        "meta": 4.0,
        "cumple_meta": promedio > 4.0 if total_calificaciones > 0 else None,
        "unidad": "escala_1_5"
    }

def getTiempoCicloAdmision() -> Dict[str, Any]:
    """
    Calcula el tiempo de ciclo de admisión
    Fórmula: Tiempo desde el login hasta la confirmación de la reserva
    Meta: <2 minutos
    """
    conn = getConnection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            AVG(EXTRACT(EPOCH FROM (reserva_confirmada_at - created_at)) / 60) as tiempo_promedio_minutos,
            COUNT(*) as total_reservas
        FROM citas
        WHERE reserva_confirmada_at IS NOT NULL 
        AND created_at IS NOT NULL
    """)
    
    row = cur.fetchone()
    conn.close()
    
    tiempo_promedio = float(row[0]) if row[0] else 0.0
    total_reservas = int(row[1]) if row[1] else 0
    
    return {
        "valor": round(tiempo_promedio, 2),
        "total_reservas": total_reservas,
        "meta": 2,
        "cumple_meta": tiempo_promedio < 2 if tiempo_promedio > 0 else None,
        "unidad": "minutos"
    }

def getAllKPIs() -> Dict[str, Any]:
    """
    Obtiene todos los KPIs en un solo objeto
    """
    return {
        "tiempo_espera_promedio": getTiempoEsperaPromedio(),
        "tasa_ausentismo": getTasaAusentismo(),
        "tasa_ocupacion_medica": getTasaOcupacionMedica(),
        "nivel_satisfaccion": getNivelSatisfaccion(),
        "tiempo_ciclo_admision": getTiempoCicloAdmision()
    }

