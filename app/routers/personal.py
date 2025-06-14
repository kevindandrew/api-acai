from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import Query
from typing import Optional
from app.database import get_db
from app.models.personal import Personal
from app.schemas.personal import (
    PersonalCreate,
    PersonalResponse,
    PersonalUpdate
)
from app.security import get_password_hash
from app.dependencies import get_current_active_user, get_current_user, require_admin

router = APIRouter(
    prefix="/personal",
    tags=["Personal"],
)


@router.post("/", response_model=PersonalResponse, status_code=status.HTTP_201_CREATED)
def crear_personal(
    personal: PersonalCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    # Verificar si el usuario ya existe
    if db.query(Personal).filter(Personal.usuario == personal.usuario).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )

    # Hashear la contraseña
    hashed_password = get_password_hash(personal.contraseña)

    db_personal = Personal(
        **personal.model_dump(exclude={"contraseña"}),
        contraseña_hash=hashed_password
    )

    db.add(db_personal)
    db.commit()
    db.refresh(db_personal)
    return db_personal


@router.get("/", response_model=List[PersonalResponse])
def listar_personal(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    sucursal_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """
    Lista personal con filtrado por sucursal.
    - **sucursal_id**: Filtrar por ID de sucursal (opcional)
    - **skip**: Registros a saltar (para paginación)
    - **limit**: Límite de resultados (max 1000)
    """
    query = db.query(Personal)

    if sucursal_id:
        query = query.filter(Personal.id_sucursal == sucursal_id)

    return query.offset(skip).limit(limit).all()


@router.get("/{personal_id}", response_model=PersonalResponse)
def obtener_personal(
    personal_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    personal = db.query(Personal).get(personal_id)
    if not personal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado"
        )
    return personal


@router.put("/{personal_id}", response_model=PersonalResponse)
def actualizar_personal(
    personal_id: int,
    personal_data: PersonalUpdate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    personal = db.query(Personal).get(personal_id)
    if not personal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado"
        )

    update_data = personal_data.model_dump(exclude_unset=True)

    if "contraseña" in update_data:
        update_data["contraseña_hash"] = get_password_hash(
            update_data.pop("contraseña"))

    for field, value in update_data.items():
        setattr(personal, field, value)

    db.commit()
    db.refresh(personal)
    return personal


@router.put(
    "/me",
    response_model=PersonalResponse
)
def actualizar_mi_perfil(
    update_data: PersonalUpdate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_active_user)
):
    """Permite a cada usuario actualizar su propio perfil"""
    if update_data.contraseña:
        update_data.contraseña_hash = get_password_hash(update_data.contraseña)
        del update_data.contraseña

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.delete("/{personal_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_personal(
    personal_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    personal = db.query(Personal).get(personal_id)
    if not personal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado"
        )

    db.delete(personal)
    db.commit()
    return None
