from datetime import date, datetime

from fastapi import HTTPException

from app.db import getConnection
from app.schemas.Citas import CitaCrear
from app.services.AuditoriaService import registrarAuditoria


def reservarCita(cita: CitaCrear):
    conn = getConnection()
    cur = conn.cursor()

    try:
        validarEstudiante(cita.estudianteId, cur)
        validarEspecialidad(cita.especialidadId, cur)
        validarMedico(cita.medicoId, cur)
        validarMedicoEspecialidad(cita.medicoId, cita.especialidadId, cur)
        validarFechaNoPasada(cita.fecha, cita.hora)
        validarDisponibilidad(cita.fecha, cita.hora, cita.medicoId, cita.especialidadId, cur)
        validarFechaHora(cita.fecha, cita.hora, cita.medicoId, cur)
        validarEstado(cita.estado)

        if cita.estado != "reservada":
            raise HTTPException(status_code=400, detail="Una cita nueva debe crearse con estado reservada.")

        hora_cita = datetime.combine(cita.fecha, cita.hora)
        ahora = datetime.now()

        cur.execute(
            """
            INSERT INTO citas (
                estudiante_id, medico_id, fecha, hora, estado, especialidad_id,
                hora_cita, created_at, reserva_confirmada_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                cita.estudianteId,
                cita.medicoId,
                cita.fecha,
                cita.hora,
                cita.estado,
                cita.especialidadId,
                hora_cita,
                ahora,
                ahora,
                ahora,
            ),
        )
        cita_id = cur.fetchone()[0]
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    conn.close()

    registrarAuditoria(
        cita.estudianteId,
        "estudiante",
        "reservar_cita",
        "citas",
        cita_id,
        f"medico_id={cita.medicoId}, fecha={cita.fecha}, hora={cita.hora}",
    )
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
        (estudianteId,),
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
            "calificacion": c[9] if c[9] else None,
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
        AND c.estado IN ('cancelada', 'atendida', 'no_asistio')
        ORDER BY c.fecha DESC, c.hora DESC
        """,
        (estudianteId,),
    )
    citas = cur.fetchall()
    conn.close()

    historial_por_especialidad = {}
    for c in citas:
        especialidad_id = c[3]
        especialidad_nombre = c[4]

        if especialidad_id not in historial_por_especialidad:
            historial_por_especialidad[especialidad_id] = {
                "especialidadId": especialidad_id,
                "especialidadNombre": especialidad_nombre,
                "citas": [],
            }

        historial_por_especialidad[especialidad_id]["citas"].append(
            {
                "citaId": c[0],
                "estudianteId": c[1],
                "medicoNombre": c[2],
                "fecha": c[5],
                "hora": c[6],
                "estado": c[7],
                "horaAtencion": c[8].isoformat() if c[8] else None,
                "tieneCalificacion": c[9] is not None,
                "calificacion": c[10] if c[10] else None,
            }
        )

    return list(historial_por_especialidad.values())


def getCitasReservadasPorEspecialidad(especialidadId: int, fecha=None):
    conn = getConnection()
    cur = conn.cursor()

    filtro_fecha = "AND c.fecha = %s" if fecha else ""
    params = [especialidadId]
    if fecha:
        params.append(fecha)

    cur.execute(
        f"""
        SELECT
            c.id,
            c.fecha,
            c.hora,
            (c.hora + (COALESCE(de.duracion_turno, 30) || ' minutes')::interval)::time as hora_fin,
            e.codigo_estudiante,
            e.nombres || ' ' || e.apellidos as estudiante_nombre,
            m.nombres || ' ' || m.apellidos as medico_nombre,
            esp.nombre as especialidad_nombre,
            ra.hora_llegada
        FROM citas c
        JOIN estudiantes e ON c.estudiante_id = e.id
        JOIN medicos m ON c.medico_id = m.id
        JOIN especialidades esp ON c.especialidad_id = esp.id
        LEFT JOIN disponibilidad_especialidad de
          ON de.especialidad_id = c.especialidad_id
         AND c.fecha BETWEEN de.fecha_inicio AND de.fecha_fin
         AND EXTRACT(ISODOW FROM c.fecha)::int = de.dia_semana
         AND c.hora >= de.hora_inicio
         AND c.hora < de.hora_fin
        LEFT JOIN registro_atencion ra ON ra.cita_id = c.id
        WHERE c.estado = 'reservada'
          AND c.especialidad_id = %s
          {filtro_fecha}
        ORDER BY c.fecha ASC, c.hora ASC, estudiante_nombre ASC
        """,
        tuple(params),
    )
    citas = cur.fetchall()
    conn.close()

    return [
        {
            "citaId": c[0],
            "fecha": c[1],
            "horaInicio": c[2],
            "horaFin": c[3],
            "codigoEstudiante": c[4],
            "nombreEstudiante": c[5],
            "nombreMedico": c[6],
            "especialidadNombre": c[7],
            "horaLlegada": c[8].isoformat() if c[8] else None,
            "registradaLlegada": c[8] is not None,
        }
        for c in citas
    ]


def getResumenCitasTopico(fecha=None):
    conn = getConnection()
    cur = conn.cursor()

    filtro_fecha = "AND c.fecha = %s" if fecha else ""
    params = [fecha] if fecha else []

    cur.execute(
        f"""
        SELECT
            e.id,
            e.nombre,
            COUNT(c.id) AS total_citas
        FROM especialidades e
        LEFT JOIN citas c
          ON c.especialidad_id = e.id
         AND c.estado = 'reservada'
         {filtro_fecha}
        WHERE e.estado = true
        GROUP BY e.id, e.nombre
        ORDER BY e.nombre ASC
        """,
        tuple(params),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "especialidadId": row[0],
            "especialidadNombre": row[1],
            "totalCitas": row[2],
        }
        for row in rows
    ]


def buscarCitaReservadaPorCodigo(codigoEstudiante: str, fecha=None):
    conn = getConnection()
    cur = conn.cursor()

    filtro_fecha = "AND c.fecha = %s" if fecha else ""
    params = [codigoEstudiante]
    if fecha:
        params.append(fecha)

    cur.execute(
        f"""
        SELECT
            c.id,
            c.fecha,
            c.hora,
            (c.hora + (COALESCE(de.duracion_turno, 30) || ' minutes')::interval)::time as hora_fin,
            e.codigo_estudiante,
            e.nombres || ' ' || e.apellidos as estudiante_nombre,
            m.nombres || ' ' || m.apellidos as medico_nombre,
            esp.id as especialidad_id,
            esp.nombre as especialidad_nombre,
            ra.hora_llegada
        FROM citas c
        JOIN estudiantes e ON c.estudiante_id = e.id
        JOIN medicos m ON c.medico_id = m.id
        JOIN especialidades esp ON c.especialidad_id = esp.id
        LEFT JOIN disponibilidad_especialidad de
          ON de.especialidad_id = c.especialidad_id
         AND c.fecha BETWEEN de.fecha_inicio AND de.fecha_fin
         AND EXTRACT(ISODOW FROM c.fecha)::int = de.dia_semana
         AND c.hora >= de.hora_inicio
         AND c.hora < de.hora_fin
        LEFT JOIN registro_atencion ra ON ra.cita_id = c.id
        WHERE c.estado = 'reservada'
          AND UPPER(e.codigo_estudiante) = UPPER(%s)
          {filtro_fecha}
        ORDER BY c.fecha ASC, c.hora ASC
        """,
        tuple(params),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "citaId": row[0],
            "fecha": row[1],
            "horaInicio": row[2],
            "horaFin": row[3],
            "codigoEstudiante": row[4],
            "nombreEstudiante": row[5],
            "nombreMedico": row[6],
            "especialidadId": row[7],
            "especialidadNombre": row[8],
            "horaLlegada": row[9].isoformat() if row[9] else None,
            "registradaLlegada": row[9] is not None,
        }
        for row in rows
    ]


def cancelarCita(citaId: int):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT id, estado FROM citas WHERE id = %s", (citaId,))
    cita = cur.fetchone()

    if cita is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    if cita[1] == "cancelada":
        conn.close()
        raise HTTPException(status_code=400, detail="La cita ya esta cancelada")

    if cita[1] != "reservada":
        conn.close()
        raise HTTPException(status_code=400, detail="Solo se puede cancelar una cita reservada")

    cur.execute(
        """
        UPDATE citas
        SET estado = 'cancelada', updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING estudiante_id
        """,
        (citaId,),
    )
    estudiante_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    registrarAuditoria(estudiante_id, "estudiante", "cancelar_cita", "citas", citaId)
    return {"message": "Cita cancelada exitosamente"}


def validarEstudiante(estudianteId: int, cur):
    cur.execute("SELECT id FROM estudiantes WHERE id = %s", (estudianteId,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail=f"Estudiante con ID {estudianteId} no existe.")


def validarEspecialidad(especialidadId: int, cur):
    cur.execute("SELECT id FROM especialidades WHERE id = %s", (especialidadId,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail=f"Especialidad con ID {especialidadId} no existe.")


def validarMedico(medicoId: int, cur):
    cur.execute("SELECT id FROM medicos WHERE id = %s", (medicoId,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail=f"Medico con ID {medicoId} no existe.")


def validarMedicoEspecialidad(medicoId: int, especialidadId: int, cur):
    cur.execute(
        "SELECT id FROM medicos WHERE id = %s AND especialidad_id = %s",
        (medicoId, especialidadId),
    )
    if cur.fetchone() is None:
        raise HTTPException(status_code=400, detail="El medico no pertenece a la especialidad seleccionada.")


def validarFechaNoPasada(fecha, hora):
    if fecha < date.today():
        raise HTTPException(status_code=400, detail="No se puede reservar una cita en una fecha pasada.")

    if datetime.combine(fecha, hora) <= datetime.now():
        raise HTTPException(status_code=400, detail="No se puede reservar una cita en una hora que ya paso.")


def validarDisponibilidad(fecha, hora, medicoId, especialidadId, cur):
    cur.execute(
        """
        SELECT 1
        FROM medicos m
        JOIN disponibilidad_especialidad de
          ON de.especialidad_id = m.especialidad_id
        WHERE m.id = %s
          AND de.especialidad_id = %s
          AND %s::date BETWEEN de.fecha_inicio AND de.fecha_fin
          AND EXTRACT(ISODOW FROM %s::date)::int = de.dia_semana
          AND %s::time >= de.hora_inicio
          AND %s::time < de.hora_fin
          AND de.disponibilidad = true
        """,
        (medicoId, especialidadId, fecha, fecha, hora, hora),
    )
    if cur.fetchone() is None:
        raise HTTPException(status_code=400, detail="El medico no tiene disponibilidad en la fecha y hora seleccionadas.")


def validarFechaHora(fecha, hora, medicoId, cur):
    cur.execute(
        """
        SELECT id
        FROM citas
        WHERE fecha = %s
          AND hora = %s
          AND medico_id = %s
          AND estado = 'reservada'
        """,
        (fecha, hora, medicoId),
    )
    if cur.fetchone() is not None:
        raise HTTPException(status_code=409, detail="Ya existe una cita reservada para ese medico en ese horario.")


def validarEstado(estado: str):
    estados_validos = ["reservada", "cancelada", "atendida", "no_asistio"]
    if estado not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado '{estado}' no es valido.")
