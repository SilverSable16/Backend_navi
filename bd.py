import os
import psycopg2

def conectar():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )


def obtener_reglas():
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("SELECT antecedente, consecuente FROM reglas")
        return cur.fetchall()

def obtener_ejemplos_para_entrenar():
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT e.texto, i.etiqueta
            FROM ejemplos_usuario e
            JOIN intenciones i ON e.intencion_id = i.id
        """)
        return cur.fetchall()

def obtener_respuesta_por_etiqueta(etiqueta):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT texto, explicacion
            FROM respuestas r
            JOIN intenciones i ON r.intencion_id = i.id
            WHERE i.etiqueta = %s
            LIMIT 1
        """, (etiqueta,))
        return cur.fetchone()

def obtener_id_intencion(etiqueta):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM intenciones WHERE etiqueta = %s", (etiqueta,))
        row = cur.fetchone()
        return row[0] if row else None

def crear_intencion(etiqueta, descripcion="Intención aprendida automáticamente"):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO intenciones (etiqueta, descripcion) VALUES (%s, %s) RETURNING id",
                    (etiqueta, descripcion))
        return cur.fetchone()[0]

def insertar_ejemplo(texto, intencion_id):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO ejemplos_usuario (texto, intencion_id) VALUES (%s, %s)",
                    (texto, intencion_id))

def insertar_respuesta(intencion_id, texto, explicacion):
    with conectar() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO respuestas (intencion_id, texto, explicacion) VALUES (%s, %s, %s)",
                    (intencion_id, texto, explicacion))
