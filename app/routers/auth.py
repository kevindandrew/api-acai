from sqlite3 import OperationalError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.personal import Personal
from app.schemas.auth import AuthResponse, UserLogin
from app.schemas.personal import PersonalResponse
from app.security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.dependencies import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        401: {"description": "Credenciales inválidas"},
        500: {"description": "Error interno del servidor"}
    }
)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Autenticar usuario",
    description="Verifica credenciales y devuelve token JWT"
)
async def login(
    usuario: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autentica un usuario y genera un token de acceso.

    - **username**: Nombre de usuario (entre 3 y 30 caracteres)
    - **password**: Contraseña (mínimo 6 caracteres)
    """
    try:
        # 1. Buscar usuario
        user = db.query(Personal).filter(
            Personal.usuario == usuario.username
        ).first()

        # 2. Verificar credenciales
        if not user or not verify_password(usuario.password, user.contraseña_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # 3. Generar token (incluye rol y sucursal para autorización)
        token_data = {
            "sub": user.usuario,
            "rol": user.rol.nombre,  # Asume relación con tabla Roles
            "sucursal_id": user.id_sucursal
        }
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # 4. Actualizar último login (opcional)
        user.fecha_ultimo_login = datetime.utcnow()
        db.commit()

        # 5. Retornar respuesta estándar
        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=PersonalResponse.from_orm(user)
        )

    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error de conexión con la base de datos"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )


@router.get(
    "/me",
    response_model=PersonalResponse,
    summary="Obtener usuario actual",
    description="Devuelve los datos del usuario autenticado"
)
async def read_current_user(current_user: Personal = Depends(get_current_user)):
    """
    Devuelve la información del usuario autenticado mediante el token.
    """
    return PersonalResponse.from_orm(current_user)
