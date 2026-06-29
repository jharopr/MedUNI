from datetime import date

from app.db import getConnection


def genHorarios(dia: date, medicoId: int):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT de.hora_inicio, de.hora_fin, de.duracion_turno
        FROM disponibilidad_especialidad de
        INNER JOIN medicos me
            ON me.especialidad_id = de.especialidad_id
        WHERE EXTRACT(ISODOW FROM %s::date) = de.dia_semana
          AND %s::date BETWEEN de.fecha_inicio AND de.fecha_fin
          AND de.disponibilidad = true
          AND me.id = %s
        ORDER BY de.hora_inicio
        LIMIT 1
        """,
        (dia, dia, medicoId),
    )
    horas_limite = cursor.fetchone()

    cursor.close()
    if not horas_limite:
        conn.close()
        return []

    hora_inicio = horas_limite[0]
    hora_final = horas_limite[1]
    duracion_turno = horas_limite[2] or 30

    cursor = conn.cursor()
    cursor.execute(
        """
        WITH horarios AS (
            SELECT
                generate_series(
                    ('2025-09-05 ' || %s)::timestamp,
                    ('2025-09-05 ' || %s)::timestamp - (%s || ' minutes')::interval,
                    (%s || ' minutes')::interval
                ) AS hora_inicio
        )
        SELECT
            hora_inicio::time AS hora_inicio,
            (hora_inicio + (%s || ' minutes')::interval)::time AS hora_final,
            CASE
                WHEN c.id IS NOT NULL THEN FALSE
                ELSE TRUE
            END AS disponibilidad
        FROM horarios h
        LEFT JOIN citas c
            ON c.medico_id = %s
            AND c.fecha = %s
            AND c.hora = hora_inicio::time
            AND c.estado = 'reservada'
        ORDER BY hora_inicio
        """,
        (hora_inicio, hora_final, duracion_turno, duracion_turno, duracion_turno, medicoId, dia),
    )
    horarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {"horaInicio": horario[0], "horaFin": horario[1], "disponibilidad": horario[2]}
        for horario in horarios
    ]
