
import sqlite3

from app.config import DB_NAME


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        # Tabla de usuarios.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                picture TEXT
            )
        """)

        # Catálogo de roles.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
            )
        """)

        # Relación entre usuarios y roles.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario_roles (
                usuario_id INTEGER NOT NULL,
                rol_id INTEGER NOT NULL,

                PRIMARY KEY (usuario_id, rol_id),

                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (rol_id)
                    REFERENCES roles(id)
                    ON DELETE CASCADE
            )
        """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS solicitudes_trabajo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                correo TEXT NOT NULL,
                nombre_discord TEXT NOT NULL,
                puesto_principal TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'PENDIENTE',
                fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  
                FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id)
                ON DELETE CASCADE
            )
        """)




        # Roles disponibles en el sistema.
        cursor.executemany(
            """
            INSERT OR IGNORE INTO roles (nombre)
            VALUES (?)
            """,
            [
                ("USUARIO",),
                ("EDITOR",),
                ("ADMIN",),
            ],
        )

        # Garantiza que los cambios se guarden.
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
