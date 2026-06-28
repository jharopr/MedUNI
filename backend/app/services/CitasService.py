from app.schemas.Citas import CitaCrear
from fastapi import HTTPException
from app.db import getConnection  # tu conexión psycopg

def reservarCita(cita: CitaCrear):
        from datetime import datetime
        conn = getConnection()
        cur = conn.cursor()
    #---------VALIDACIONES---------------------
        validarEstudiante(cita.estudianteId, cur)
        validarEspecialidad(cita.especialidadId, cur)
        validarMedico(cita.medicoId, cur)
        validarFechaHora(cita.fecha, cita.hora, cita.medicoId, cur)
        validarEstado(cita.estado)
        #------------------------------------------
        # Crear timestamp de la cita (fecha + hora)
        hora_cita = datetime.combine(cita.fecha, cita.hora)
        ahora = datetime.now()
        
        cur.execute(
            """INSERT INTO citas (estudiante_id, medico_id, fecha, hora, estado, especialidad_id, hora_cita, created_at, reserva_confirmada_at) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (cita.estudianteId, cita.medicoId, cita.fecha, cita.hora, cita.estado, cita.especialidadId, hora_cita, ahora, ahora)
        )
        conn.commit()
        conn.close()
        return cita

def getCitasReservadas(estudianteId: int):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.estudiante_id, m.nombres, e.nombre, c.fecha, c.hora, c.estado, 
               c.hora_atencion, cal.id as calificacion_id, cal.calificacion
        FROM citas c
        JOIN medicos m ON c.medico_id = m.id
        JOIN especialidades e ON m.especialidad_id = e.id
        LEFT JOIN calificaciones cal ON c.id = cal.cita_id
        WHERE c.estudiante_id = %s AND c.estado = 'reservada'
        ORDER BY c.fecha DESC, c.hora DESC
        """,
        (estudianteId,)
    )
    citas = cur.fetchall()
    conn.close()
    return [
        {
            "citaId": c[0],
            "estudianteId": c[1],
            "medicoNombre": c[2],
            "especialidadNombre": c[3],
            "fecha": c[4],
            "hora": c[5],
            "estado": c[6],
            "horaAtencion": c[7].isoformat() if c[7] else None,
            "tieneCalificacion": c[8] is not None,
            "calificacion": c[9] if c[9] else None
        }
        for c in citas
    ]

def getHistorialCitasPorEspecialidad(estudianteId: int):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.estudiante_id, m.nombres || ' ' || m.apellidos as medico_nombre, 
               e.id as especialidad_id, e.nombre as especialidad_nombre, 
               c.fecha, c.hora, c.estado, c.hora_atencion,
               cal.id as calificacion_id, cal.calificacion
        FROM citas c
        JOIN medicos m ON c.medico_id = m.id
        JOIN especialidades e ON c.especialidad_id = e.id
        LEFT JOIN calificaciones cal ON c.id = cal.cita_id
        WHERE c.estudiante_id = %s 
        AND c.estado IN ('cancelada', 'atendida')
        ORDER BY c.fecha DESC, c.hora DESC
        """,
        (estudianteId,)
    )
    citas = cur.fetchall()
    conn.close()
    
    # Agrupar por especialidad
    historial_por_especialidad = {}
    for c in citas:
        especialidad_id = c[3]
        especialidad_nombre = c[4]
        
        if especialidad_id not in historial_por_especialidad:
            historial_por_especialidad[especialidad_id] = {
                "especialidadId": especialidad_id,
                "especialidadNombre": especialidad_nombre,
                "citas": []
            }
        
        historial_por_especialidad[especialidad_id]["citas"].append({
            "citaId": c[0],
            "estudianteId": c[1],
            "medicoNombre": c[2],
            "fecha": c[5],
            "hora": c[6],
            "estado": c[7],
            "horaAtencion": c[8].isoformat() if c[8] else None,
            "tieneCalificacion": c[9] is not None,
            "calificacion": c[10] if c[10] else None
        })
    
    return list(historial_por_especialidad.values())

def cancelarCita(citaId:int):
    conn = getConnection()
    cur = conn.cursor()
    # Validar si la cita existe y está reservada
    cur.execute("SELECT id, estado FROM citas WHERE id = %s", (citaId,))
    cita = cur.fetchone()

    if cita is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    if cita[1] == 'cancelada':
        conn.close()
        raise HTTPException(status_code=400, detail="La cita ya está cancelada")

    # Cambiar el estado a cancelada en lugar de eliminar
    cur.execute("UPDATE citas SET estado = 'cancelada' WHERE id = %s", (citaId,))
    conn.commit()
    conn.close()

    return {"message": "Cita cancelada exitosamente"}

# Validaciones
def validarEstudiante(estudianteId: int, cur):
    cur.execute("SELECT id FROM estudiantes WHERE id = %s", (estudianteId,))
    if cur.fetchone() is None:
        raise ValueError(f"Estudiante con ID {estudianteId} no existe.")

def validarEspecialidad(especialidadId: int, cur):
    cur.execute("SELECT id FROM especialidades WHERE id = %s", (especialidadId,))
    if cur.fetchone() is None:
        raise ValueError(f"Especialidad con ID {especialidadId} no existe.")

def validarMedico(medicoId: int, cur):
    cur.execute("SELECT id FROM medicos WHERE id = %s", (medicoId,))
    if cur.fetchone() is None:
        raise ValueError(f"Médico con ID {medicoId} no existe.")

def validarFechaHora(fecha, hora, medicoId, cur):
    cur.execute("SELECT id FROM citas WHERE fecha = %s AND hora = %s AND medico_id = %s AND estado = 'reservada'", (fecha, hora, medicoId))
    if cur.fetchone() is not None:
        raise ValueError(f"Ya existe una cita reservada para {fecha} a las {hora} para el medico seleccionado.")

def validarEstado(estado: str):
    estados_validos = ["reservada", "cancelada", "atendida"]
    if estado not in estados_validos:
        raise ValueError(f"Estado '{estado}' no es válido. Estados permitidos: {', '.join(estados_validos)}.")