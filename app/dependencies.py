from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.security import (
    security,
    verify_access_token,
    get_db
)
from app.models.personal import Personal


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Personal:
    """Obtiene el usuario actual desde el token JWT."""
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Personal).filter(Personal.usuario == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user


async def get_current_active_user(
    current_user: Personal = Depends(get_current_user)
) -> Personal:
    """Versión simplificada sin verificación de estado activo"""
    return current_user


def require_role(*role_names: str):
    """Permite múltiples roles (ej: Admin o Encargado)."""
    async def roles_checker(
        current_user: Personal = Depends(get_current_active_user)
    ) -> Personal:
        if current_user.rol.nombre.lower() not in [r.lower() for r in role_names]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los siguientes roles: {', '.join(role_names)}"
            )
        return current_user
    return roles_checker


# Dependencias predefinidas
require_admin = require_role("Administrador")
require_encargado = require_role("Gerente Sucursal")
require_vendedor = require_role("Vendedor")
require_admin_or_encargado = require_role("Administrador", "Gerente Sucursal")


def require_sucursal(sucursal_id: int = None):
    """Verifica acceso a una sucursal específica."""
    async def sucursal_checker(
        current_user: Personal = Depends(get_current_active_user)
    ) -> Personal:
        if current_user.rol.nombre.lower() == "administrador":
            return current_user

        if sucursal_id and current_user.id_sucursal != sucursal_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta sucursal"
            )
        return current_user
    return sucursal_checker
