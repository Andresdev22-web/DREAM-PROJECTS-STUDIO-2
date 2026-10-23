
from collections.abc import Sequence

import jwt
from fastapi import Depends, Header, HTTPException, status

from app.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.services.auth_service import get_user_by_id


def get_current_user(
    authorization: str | None = Header(default=None),
) -> dict:
    # 1. Comprueba que se haya enviado el encabezado Authorization.
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Exige el formato: Bearer <token>.
    scheme, separator, token = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autenticación inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verifica la firma y la expiración del JWT.
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )

        user_id = int(payload["sub"])

    except (
        jwt.InvalidTokenError,
        ValueError,
        KeyError,
        TypeError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Recupera el usuario y sus roles actuales desde SQLite.
    user = get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario ya no existe.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_roles(
    allowed_roles: Sequence[str],
):
    # Normaliza los roles requeridos.
    normalized_roles = {
        role.strip().upper()
        for role in allowed_roles
        if role.strip()
    }

    if not normalized_roles:
        raise ValueError(
            "Debes especificar al menos un rol permitido."
        )

    def role_checker(
        user: dict = Depends(get_current_user),
    ) -> dict:
        # Obtiene los roles actuales del usuario.
        user_roles = set(user.get("roles", []))

        # Basta con tener uno de los roles permitidos.
        if not user_roles.intersection(normalized_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "mensaje": "No tienes permisos para esta operación.",
                    "roles_permitidos": sorted(normalized_roles),
                },
            )

        # Devuelve el usuario para utilizarlo en la ruta.
        return user

    return role_checker
