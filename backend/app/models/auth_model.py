
from pydantic import BaseModel, ConfigDict


class GoogleLoginRequest(BaseModel):
    # Token de identidad obtenido por el frontend desde Google.
    token: str


class UserResponse(BaseModel):
    # Información pública del usuario autenticado.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    picture: str | None = None

    # Roles actuales del usuario.
    roles: list[str]


class TokenResponse(BaseModel):
    # JWT emitido por nuestra propia API.
    access_token: str
    token_type: str = "bearer"

    # Perfil del usuario autenticado.
    user: UserResponse
