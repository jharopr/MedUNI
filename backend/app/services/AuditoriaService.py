from app.db import getConnection
from fastapi import HTTPException


def registrarAuditoria(usuario_id, rol: str, accion: str, entidad: str, entidad_id=None, detalle: str = None):
    conn = getConnection()
    if not conn:
        return

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO auditoria (usuario_id, rol, accion, entidad, entidad_id, detalle)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (usuario_id, rol, accion, entidad, entidad_id, detalle),
        )
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()


def listarAuditoria(rol=None, accion=None, fecha_desde=None, fecha_hasta=None, limit: int = 100):
    conn = getConnection()
    if not conn:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")

    limit = max(1, min(limit, 300))
    filtros = []
    params = []

    if rol and rol != "todos":
        filtros.append("a.rol = %s")
        params.append(rol)

    if accion:
        filtros.append("LOWER(a.accion) LIKE LOWER(%s)")
        params.append(f"%{accion}%")

    if fecha_desde:
        filtros.append("a.fecha::date >= %s")
        params.append(fecha_desde)

    if fecha_hasta:
        filtros.append("a.fecha::date <= %s")
        params.append(fecha_hasta)

    where_sql = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT
                a.id,
                a.usuario_id,
                a.rol,
                a.accion,
                a.entidad,
                a.entidad_id,
                a.fecha,
                a.detalle,
                CASE
                    WHEN a.rol = 'medico' THEN COALESCE(m.nombres || ' ' || m.apellidos, 'Medico no encontrado')
                    WHEN a.rol = 'topico' THEN COALESCE(pt.nombres || ' ' || pt.apellidos, 'Topico no encontrado')
                    WHEN a.rol = 'estudiante' THEN COALESCE(e.nombres || ' ' || e.apellidos, 'Estudiante no encontrado')
                    WHEN a.rol = 'administrador' THEN COALESCE(ad.nombres || ' ' || ad.apellidos, 'Administrador no encontrado')
                    ELSE 'Usuario no identificado'
                END AS usuario_nombre,
                CASE
                    WHEN a.rol = 'medico' THEN m.correo
                    WHEN a.rol = 'topico' THEN pt.correo
                    WHEN a.rol = 'estudiante' THEN e.correo
                    WHEN a.rol = 'administrador' THEN ad.correo
                    ELSE NULL
                END AS usuario_correo,
                CASE
                    WHEN a.rol = 'estudiante' THEN e.codigo_estudiante
                    ELSE NULL
                END AS codigo_estudiante
            FROM auditoria a
            LEFT JOIN medicos m ON a.rol = 'medico' AND m.id = a.usuario_id
            LEFT JOIN personal_topico pt ON a.rol = 'topico' AND pt.id = a.usuario_id
            LEFT JOIN estudiantes e ON a.rol = 'estudiante' AND e.id = a.usuario_id
            LEFT JOIN administradores ad ON a.rol = 'administrador' AND ad.id = a.usuario_id
            {where_sql}
            ORDER BY a.fecha DESC, a.id DESC
            LIMIT %s
            """,
            tuple(params + [limit]),
        )
        rows = cur.fetchall()

        cur.execute(
            f"""
            SELECT a.rol, COUNT(*) AS total
            FROM auditoria a
            {where_sql}
            GROUP BY a.rol
            ORDER BY a.rol
            """,
            tuple(params),
        )
        resumen_rows = cur.fetchall()
    finally:
        conn.close()

    resumen = {"medico": 0, "topico": 0, "estudiante": 0, "administrador": 0}
    for row in resumen_rows:
        resumen[row[0] or "sin_rol"] = row[1]

    return {
        "resumen": resumen,
        "total": sum(resumen.values()),
        "items": [
            {
                "id": row[0],
                "usuarioId": row[1],
                "rol": row[2],
                "accion": row[3],
                "entidad": row[4],
                "entidadId": row[5],
                "fecha": row[6].isoformat() if row[6] else None,
                "detalle": row[7],
                "usuarioNombre": row[8],
                "usuarioCorreo": row[9],
                "codigoEstudiante": row[10],
            }
            for row in rows
        ],
    }
