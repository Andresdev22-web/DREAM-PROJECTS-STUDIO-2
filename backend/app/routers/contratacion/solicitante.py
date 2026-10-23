
from fastapi import APIRouter, Depends

from app.database import get_db_connection
from app.dependencies.auth import get_current_user
from app.models.contratacion.solicitante import SolicitudCreate


router = APIRouter(
    prefix="/solicitudes-trabajo",
    tags=["Solicitudes de trabajo"],
)

# esperamos el jwt de autenticacion  y los datos enviados para crear la solicitud
# devolvemos
@router.post("/crear")
def crear_solicitud(
    datos: SolicitudCreate,
    usuario: dict = Depends(get_current_user),
):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO solicitudes_trabajo (
                usuario_id,
                correo,
                nombre_discord,
                puesto_principal
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                usuario["id"],
                datos.correo,
                datos.nombre_discord,
                datos.puesto_principal
            ),
        )

        conn.commit()

        return {
            "mensaje": "Solicitud enviada correctamente",
            "id": cursor.lastrowid,
        }

    finally:
        conn.close()



@router.get("/buscar")
def buscar_solicitudes_usuario(
    usuario: dict = Depends(get_current_user),
):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                correo,
                nombre_discord,
                estado,
                fecha_creacion,
                Puesto_principal
            FROM solicitudes_trabajo
            WHERE usuario_id = ?
            ORDER BY id DESC
            """,
            (usuario["id"],),
        )

        filas = cursor.fetchall()
        columnas = [columna[0] for columna in cursor.description]

        return [
            dict(zip(columnas, fila))
            for fila in filas
        ]

    finally:
        conn.close()

























# ruta publica para testing

# Ruta pública para testing
@router.get("/test")
def listar_solicitudes_publicas():
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombre_discord , estado , fecha_creacion , Puesto_principal
            FROM solicitudes_trabajo
            ORDER BY id DESC
        """)

        filas = cursor.fetchall()

        columnas = [columna[0] for columna in cursor.description]

        return [
            dict(zip(columnas, fila))
            for fila in filas
        ]

    finally:
        conn.close()


@router.get("/aceptar/{solicitud_id}")
def aceptar_solicitud(solicitud_id: int):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE solicitudes_trabajo
            SET estado = ?
            WHERE id = ?
            """,
            ("RECHAZADO", solicitud_id),
        )

        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="La solicitud no existe",
            )

        return {
            "mensaje": "Solicitud rechasada correctamente",
            "solicitud_id": solicitud_id,
            "estado": "RECHAZADO",
        }

    finally:
        conn.close()