from datetime import date, datetime

from fastapi import HTTPException

from app.db import getConnection
from app.services.AuditoriaService import registrarAuditoria


def listarCitasMedico(medico_id: int, fecha: date):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            c.id,
            c.fecha,
            c.hora,
            (c.hora + (COALESCE(de.duracion_turno, 30) || ' minutes')::interval)::time as hora_fin,
            e.codigo_estudiante,
            e.nombres || ' ' || e.apellidos as estudiante_nombre,
            esp.nombre as especialidad_nombre,
            ra.hora_llegada,
            ra.hora_inicio,
            ra.hora_fin,
            COALESCE(ra.estado_atencion, 'pendiente_llegada') as estado_atencion
        FROM citas c
        JOIN estudiantes e ON e.id = c.estudiante_id
        JOIN especialidades esp ON esp.id = c.especialidad_id
        LEFT JOIN disponibilidad_especialidad de
          ON de.especialidad_id = c.especialidad_id
         AND c.fecha BETWEEN de.fecha_inicio AND de.fecha_fin
         AND EXTRACT(ISODOW FROM c.fecha)::int = de.dia_semana
         AND c.hora >= de.hora_inicio
         AND c.hora < de.hora_fin
        LEFT JOIN registro_atencion ra ON ra.cita_id = c.id
        WHERE c.medico_id = %s
          AND c.fecha = %s
          AND c.estado = 'reservada'
        ORDER BY c.hora ASC, estudiante_nombre ASC
        """,
        (medico_id, fecha),
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
            "especialidadNombre": row[6],
            "horaLlegada": row[7].isoformat() if row[7] else None,
            "horaInicioAtencion": row[8].isoformat() if row[8] else None,
            "horaFinAtencion": row[9].isoformat() if row[9] else None,
            "estadoAtencion": row[10],
            "llego": row[7] is not None,
            "enAtencion": row[8] is not None and row[9] is None,
        }
        for row in rows
    ]


def iniciarCitaMedico(cita_id: int, medico_id: int):
    conn = getConnection()
    cur = conn.cursor()

    _validar_cita_medico(cur, cita_id, medico_id)

    cur.execute(
        """
        SELECT id, hora_llegada, hora_inicio, hora_fin
        FROM registro_atencion
        WHERE cita_id = %s
        """,
        (cita_id,),
    )
    registro = cur.fetchone()

    if registro is None or registro[1] is None:
        conn.close()
        raise HTTPException(status_code=400, detail="No se puede iniciar la cita porque el paciente aun no registro llegada.")

    if registro[3] is not None:
        conn.close()
        raise HTTPException(status_code=400, detail="La cita ya fue finalizada.")

    if registro[2] is not None:
        conn.close()
        raise HTTPException(status_code=400, detail="La cita ya fue iniciada.")

    ahora = datetime.now()
    cur.execute(
        """
        UPDATE registro_atencion
        SET hora_inicio = %s,
            estado_atencion = 'en_atencion',
            updated_at = %s
        WHERE cita_id = %s
        RETURNING id
        """,
        (ahora, ahora, cita_id),
    )
    registro_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    registrarAuditoria(medico_id, "medico", "iniciar_cita", "registro_atencion", registro_id, f"cita_id={cita_id}")
    return {"message": "Cita iniciada", "hora_inicio": ahora}


def finalizarCitaMedico(cita_id: int, medico_id: int):
    conn = getConnection()
    cur = conn.cursor()

    _validar_cita_medico(cur, cita_id, medico_id)

    cur.execute(
        """
        SELECT id, hora_inicio, hora_fin
        FROM registro_atencion
        WHERE cita_id = %s
        """,
        (cita_id,),
    )
    registro = cur.fetchone()

    if registro is None or registro[1] is None:
        conn.close()
        raise HTTPException(status_code=400, detail="No se puede finalizar una cita que no fue iniciada.")

    if registro[2] is not None:
        conn.close()
        raise HTTPException(status_code=400, detail="La cita ya fue finalizada.")

    ahora = datetime.now()
    cur.execute(
        """
        UPDATE registro_atencion
        SET hora_fin = %s,
            estado_atencion = 'finalizada',
            updated_at = %s
        WHERE cita_id = %s
        RETURNING id
        """,
        (ahora, ahora, cita_id),
    )
    registro_id = cur.fetchone()[0]
    cur.execute(
        """
        UPDATE citas
        SET estado = 'atendida',
            hora_atencion = COALESCE(hora_atencion, %s),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (registro[1], cita_id),
    )
    conn.commit()
    conn.close()

    registrarAuditoria(medico_id, "medico", "finalizar_cita", "registro_atencion", registro_id, f"cita_id={cita_id}")
    return {"message": "Cita finalizada", "hora_fin": ahora}


def _validar_cita_medico(cur, cita_id: int, medico_id: int):
    cur.execute(
        "SELECT id FROM citas WHERE id = %s AND medico_id = %s AND estado = 'reservada'",
        (cita_id, medico_id),
    )
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail="Cita reservada no encontrada para este medico.")
