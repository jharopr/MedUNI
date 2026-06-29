from datetime import datetime

from fastapi import HTTPException

from app.db import getConnection
from app.schemas.RegistroAtencion import RegistroAtencionActualizar, RegistroAtencionCrear
from app.services.AuditoriaService import registrarAuditoria


def _row_to_dict(row):
    if row is None:
        return None

    return {
        "id": row[0],
        "cita_id": row[1],
        "hora_llegada": row[2],
        "hora_triaje": row[3],
        "hora_inicio": row[4],
        "hora_fin": row[5],
        "estado_atencion": row[6],
        "observacion": row[7],
        "created_at": row[8],
        "updated_at": row[9],
    }


def obtenerRegistroAtencion(cita_id: int):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, cita_id, hora_llegada, hora_triaje, hora_inicio, hora_fin,
               estado_atencion, observacion, created_at, updated_at
        FROM registro_atencion
        WHERE cita_id = %s
        """,
        (cita_id,),
    )
    row = cur.fetchone()
    conn.close()
    return _row_to_dict(row)


def registrarLlegada(data: RegistroAtencionCrear, usuario_id: int = None, rol: str = "administrador"):
    conn = getConnection()
    cur = conn.cursor()

    cur.execute("SELECT id, estado FROM citas WHERE id = %s", (data.cita_id,))
    cita = cur.fetchone()
    if cita is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    if cita[1] != "reservada":
        conn.close()
        raise HTTPException(status_code=400, detail="Solo se puede registrar llegada de una cita reservada")

    ahora = datetime.now()
    cur.execute(
        """
        INSERT INTO registro_atencion (cita_id, hora_llegada, estado_atencion, observacion, updated_at)
        VALUES (%s, %s, 'en_espera', %s, %s)
        ON CONFLICT (cita_id) DO UPDATE SET
            hora_llegada = COALESCE(registro_atencion.hora_llegada, EXCLUDED.hora_llegada),
            estado_atencion = 'en_espera',
            observacion = COALESCE(EXCLUDED.observacion, registro_atencion.observacion),
            updated_at = EXCLUDED.updated_at
        RETURNING id, cita_id, hora_llegada, hora_triaje, hora_inicio, hora_fin,
                  estado_atencion, observacion, created_at, updated_at
        """,
        (data.cita_id, ahora, data.observacion, ahora),
    )
    row = cur.fetchone()
    conn.commit()
    conn.close()

    registrarAuditoria(usuario_id, rol, "registrar_llegada", "registro_atencion", row[0], f"cita_id={data.cita_id}")
    return _row_to_dict(row)


def actualizarRegistroAtencion(cita_id: int, data: RegistroAtencionActualizar, usuario_id: int = None, rol: str = "administrador"):
    conn = getConnection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM registro_atencion WHERE cita_id = %s", (cita_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Registro de atencion no encontrado")

    cur.execute(
        """
        UPDATE registro_atencion
        SET
            hora_llegada = COALESCE(%s, hora_llegada),
            hora_triaje = COALESCE(%s, hora_triaje),
            hora_inicio = COALESCE(%s, hora_inicio),
            hora_fin = COALESCE(%s, hora_fin),
            estado_atencion = COALESCE(%s, estado_atencion),
            observacion = COALESCE(%s, observacion),
            updated_at = %s
        WHERE cita_id = %s
        RETURNING id, cita_id, hora_llegada, hora_triaje, hora_inicio, hora_fin,
                  estado_atencion, observacion, created_at, updated_at
        """,
        (
            data.hora_llegada,
            data.hora_triaje,
            data.hora_inicio,
            data.hora_fin,
            data.estado_atencion,
            data.observacion,
            datetime.now(),
            cita_id,
        ),
    )
    row = cur.fetchone()

    if data.hora_fin is not None or data.estado_atencion == "finalizada":
        cur.execute(
            """
            UPDATE citas
            SET estado = 'atendida',
                hora_atencion = COALESCE(%s, hora_atencion),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (data.hora_inicio or data.hora_fin, cita_id),
        )
    elif data.estado_atencion == "no_asistio":
        cur.execute(
            "UPDATE citas SET estado = 'no_asistio', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (cita_id,),
        )

    conn.commit()
    conn.close()

    registrarAuditoria(usuario_id, rol, "actualizar_registro_atencion", "registro_atencion", row[0], f"cita_id={cita_id}")
    return _row_to_dict(row)
