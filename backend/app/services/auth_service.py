
from datetime import datetime, timedelta, timezone

import jwt
from google.auth.transport import requests
from google.oauth2 import id_token

from app.config import (
    GOOGLE_CLIENT_ID,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.database import get_db_connection


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, email, nombre, picture
            FROM usuarios
            WHERE id = ?
            """,
            (user_id,),
        )

        row = cursor.fetchone()

        if not row:
            return None

        user = dict(row)

        cursor.execute(
            """
            SELECT r.nombre
            FROM roles r
            JOIN usuario_roles ur ON ur.rol_id = r.id
            WHERE ur.usuario_id = ?
            ORDER BY r.nombre
            """,
            (user_id,),
        )

        user["roles"] = [
            row["nombre"] for row in cursor.fetchall()
        ]

        return user

    finally:
        conn.close()


def verify_google_token(token: str) -> dict:
    info = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        GOOGLE_CLIENT_ID,
    )

    if not info.get("email") or info.get("email_verified") is not True:
        raise ValueError("El correo de Google no está verificado.")

    return info


def authenticate_google_user(google_token: str) -> dict:
    # Verifica que el token pertenezca a una identidad válida de Google.
    info = verify_google_token(google_token)

    email = info["email"]
    nombre = info.get("name") or "Usuario"
    picture = info.get("picture") or ""

    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        # Crea al usuario o actualiza su perfil sin modificar sus roles.
        cursor.execute(
            """
            INSERT INTO usuarios (email, nombre, picture)
            VALUES (?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                nombre = excluded.nombre,
                picture = excluded.picture
            """,
            (email, nombre, picture),
        )

        cursor.execute(
            "SELECT id FROM usuarios WHERE email = ?",
            (email,),
        )

        user_id = cursor.fetchone()["id"]

        # Asigna el rol USUARIO únicamente si todavía no tiene roles.
        cursor.execute(
            """
            INSERT OR IGNORE INTO usuario_roles (usuario_id, rol_id)
            SELECT ?, id
            FROM roles
            WHERE nombre = 'USUARIO'
              AND NOT EXISTS (
                  SELECT 1
                  FROM usuario_roles
                  WHERE usuario_id = ?
              )
            """,
            (user_id, user_id),
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    # Recupera el perfil y los roles desde la base de datos.
    user = get_user_by_id(user_id)

    if not user:
        raise RuntimeError("No se pudo recuperar el usuario.")

    # Emite un JWT propio de nuestra API.
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user["id"]),
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    access_token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
