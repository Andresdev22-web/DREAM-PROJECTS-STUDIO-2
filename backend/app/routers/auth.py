
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.auth_model import (
    GoogleLoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import authenticate_google_user
from app.dependencies.auth import get_current_user, require_roles


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/google",
    response_model=TokenResponse,
)
def login_google(payload: GoogleLoginRequest):
    """
    RECIBE:
        Un token de identidad de Google en el cuerpo de la petición.

    DEVUELVE:
        El JWT de nuestra API, el tipo de token y el perfil del usuario
        con sus roles actuales.

    ERRORES:
        401 si el token de Google no es válido.
    """
    try:
        return authenticate_google_user(payload.token)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo verificar la identidad de Google.",
        )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    user: dict = Depends(get_current_user),
):
    """
    RECIBE:
        El encabezado Authorization: Bearer <JWT>.

    DEVUELVE:
        El perfil del usuario autenticado y sus roles actuales.

    ERRORES:
        401 si falta el token, es inválido, ha expirado o el usuario
        ya no existe.
    """
    return user


@router.get(
    "/admin",
    response_model=UserResponse,
    dependencies=[Depends(require_roles(["ADMIN"]))],
)
def admin_access(
    user: dict = Depends(get_current_user),
):
    """
    RECIBE:
        El encabezado Authorization: Bearer <JWT>.

    PERMISOS:
        Requiere el rol ADMIN.

    DEVUELVE:
        El perfil del usuario autorizado.

    ERRORES:
        401 si no está autenticado.
        403 si no tiene el rol requerido.
    """
    return user


@router.get(
    "/staff",
    response_model=UserResponse,
)
def staff_access(
    user: dict = Depends(require_roles(["ADMIN", "EDITOR"])),
):
    """
    RECIBE:
        El encabezado Authorization: Bearer <JWT>.

    PERMISOS:
        Requiere ADMIN o EDITOR. Basta con uno de los dos roles.

    DEVUELVE:
        El perfil del usuario autorizado.

    ERRORES:
        401 si no está autenticado.
        403 si no tiene ninguno de los roles permitidos.
    """
    return user
