from app.db import getConnection  # tu conexión psycopg



def loginUsuario(username: str, password: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT codigo_dirce FROM estudiantes WHERE codigo_estudiante = %s", (username,))
    row = cur.fetchone()
    conn.close()

    # Si existe y coincide la contraseña
    if row and row[0] == password:
        return True
    return False


def loginAdministrador(username: str, password: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM administradores WHERE username = %s", (username,))
    row = cur.fetchone()
    conn.close()

    # Si existe y coincide la contraseña
    if row and row[0] == password:
        return True
    return False


def loginPersonalTopico(username: str, password: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM personal_topico WHERE username = %s AND estado = true", (username,))
    row = cur.fetchone()
    conn.close()

    if row and row[0] == password:
        return True
    return False


def loginMedico(username: str, password: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM medicos WHERE username = %s AND estado = true", (username,))
    row = cur.fetchone()
    conn.close()

    if row and row[0] == password:
        return True
    return False


def getUsuario(codigo_estudiante: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombres, apellidos, correo, codigo_estudiante, codigo_dirce FROM estudiantes WHERE codigo_estudiante = %s", (codigo_estudiante,))
    row = cur.fetchone()
    conn.close()

    if row :
        # If the password matches, return a dictionary with all the user's data.
        return {
            "id": row[0],
            "nombres": row[1],
            "apellidos": row[2],
            "correo": row[3],
            "codEstudiante": row[4],
            "role": "estudiante"
        }

    # If login fails, return None.
    return None


def getAdministrador(username: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombres, apellidos, correo, username FROM administradores WHERE username = %s", (username,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nombres": row[1],
            "apellidos": row[2],
            "correo": row[3],
            "username": row[4],
            "role": "administrador"
        }

    return None


def getPersonalTopico(username: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombres, apellidos, correo, username FROM personal_topico WHERE username = %s AND estado = true", (username,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nombres": row[1],
            "apellidos": row[2],
            "correo": row[3],
            "username": row[4],
            "role": "topico"
        }

    return None


def getMedicoUsuario(username: str):
    conn = getConnection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT m.id, m.nombres, m.apellidos, m.correo, m.username,
               m.especialidad_id, e.nombre
        FROM medicos m
        JOIN especialidades e ON e.id = m.especialidad_id
        WHERE m.username = %s AND m.estado = true
        """,
        (username,),
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nombres": row[1],
            "apellidos": row[2],
            "correo": row[3],
            "username": row[4],
            "especialidadId": row[5],
            "especialidadNombre": row[6],
            "role": "medico"
        }

    return None
