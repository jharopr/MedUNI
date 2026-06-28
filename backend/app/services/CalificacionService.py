from app.db import getConnection
from app.schemas.Calificaciones import CalificacionCrear
from fastapi import HTTPException
from datetime import datetime

def crearCalificacion(calificacion: CalificacionCrear, estudiante_id: int):
    """
    Crea una calificación para una cita.
    Valida que:
    1. La cita existe
    2. La cita pertenece al estudiante
    3. La cita tiene hora_atencion (fue atendida)
    4. La cita no tiene calificación previa
    """
    conn = getConnection()
    cur = conn.cursor()
    
    try:
        # Validar que la cita existe y pertenece al estudiante
        cur.execute("""
            SELECT id, estudiante_id, hora_atencion, estado
            FROM citas 
            WHERE id = %s AND estudiante_id = %s
        """, (calificacion.cita_id, estudiante_id))
        
        cita = cur.fetchone()
        
        if cita is None:
            raise HTTPException(
                status_code=404, 
                detail="Cita no encontrada o no pertenece al estudiante"
            )
        
        # Validar que la cita fue atendida (tiene estado "atendida" y hora_atencion)
        if cita[3] != 'atendida' or cita[2] is None:
            raise HTTPException(
                status_code=400,
                detail="No se puede calificar una cita que aún no ha sido atendida"
            )
        
        # Validar que no existe calificación previa
        cur.execute("""
            SELECT id FROM calificaciones WHERE cita_id = %s
        """, (calificacion.cita_id,))
        
        if cur.fetchone() is not None:
            raise HTTPException(
                status_code=400,
                detail="Esta cita ya tiene una calificación"
            )
        
        # Insertar calificación
        cur.execute("""
            INSERT INTO calificaciones (cita_id, calificacion, comentario, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, cita_id, calificacion, comentario, created_at
        """, (
            calificacion.cita_id,
            calificacion.calificacion,
            calificacion.comentario,
            datetime.now()
        ))
        
        row = cur.fetchone()
        conn.commit()
        
        return {
            "id": row[0],
            "cita_id": row[1],
            "calificacion": row[2],
            "comentario": row[3],
            "created_at": row[4].isoformat() if row[4] else None
        }
        
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear calificación: {str(e)}"
        )
    finally:
        conn.close()

def obtenerCalificacionPorCita(cita_id: int):
    """
    Obtiene la calificación de una cita específica.
    """
    conn = getConnection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, cita_id, calificacion, comentario, created_at
            FROM calificaciones
            WHERE cita_id = %s
        """, (cita_id,))
        
        row = cur.fetchone()
        
        if row is None:
            return None
        
        return {
            "id": row[0],
            "cita_id": row[1],
            "calificacion": row[2],
            "comentario": row[3],
            "created_at": row[4].isoformat() if row[4] else None
        }
    finally:
        conn.close()

def obtenerCalificacionesPorEstudiante(estudiante_id: int):
    """
    Obtiene todas las calificaciones de las citas de un estudiante.
    """
    conn = getConnection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT c.id, c.cita_id, c.calificacion, c.comentario, c.created_at
            FROM calificaciones c
            JOIN citas cit ON c.cita_id = cit.id
            WHERE cit.estudiante_id = %s
            ORDER BY c.created_at DESC
        """, (estudiante_id,))
        
        rows = cur.fetchall()
        
        return [
            {
                "id": row[0],
                "cita_id": row[1],
                "calificacion": row[2],
                "comentario": row[3],
                "created_at": row[4].isoformat() if row[4] else None
            }
            for row in rows
        ]
    finally:
        conn.close()

