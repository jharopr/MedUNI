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
    
    # Horas programadas (basado en horarios de médicos)
    cur.execute("""
        SELECT 
            SUM(EXTRACT(EPOCH FROM (hora_fin - hora_inicio)) / 3600) as horas_programadas
        FROM horario_medico
        WHERE fecha_fin >= CURRENT_DATE
    """)
    
    horas_programadas_row = cur.fetchone()
    horas_programadas = float(horas_programadas_row[0]) if horas_programadas_row[0] else 0
    
    # Horas atendidas (basado en citas atendidas)
    cur.execute("""
        SELECT 
            COALESCE(
                SUM(EXTRACT(EPOCH FROM (ra.hora_fin - ra.hora_inicio)) / 3600),
                COUNT(c.id) * 0.5
            ) as horas_atendidas
        FROM citas c
        LEFT JOIN registro_atencion ra ON ra.cita_id = c.id
        WHERE c.estado = 'atendida'
    """)
    
    horas_atendidas_row = cur.fetchone()
    horas_atendidas = float(horas_atendidas_row[0]) if horas_atendidas_row[0] else 0
    
    conn.close()
    
    tasa = (horas_atendidas / horas_programadas * 100) if horas_programadas > 0 else 0
    
    return {
        "valor": round(tasa, 2),
        "horas_atendidas": round(horas_atendidas, 2),
        "horas_programadas": round(horas_programadas, 2),
        "meta": 85,
        "cumple_meta": tasa > 85 if horas_programadas > 0 else None,
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

