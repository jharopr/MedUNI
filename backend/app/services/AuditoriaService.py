from app.db import getConnection


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
