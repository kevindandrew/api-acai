from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.personal import Personal
from app.database import get_db
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate
from app.dependencies import require_admin, require_vendedor, get_current_user

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={404: {"description": "No encontrado"}}
)


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """Registra un nuevo cliente"""
    # Verificar CI/NIT único
    if db.query(Cliente).filter(Cliente.ci_nit == cliente.ci_nit).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El CI/NIT ya está registrado"
        )

    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    ci_nit: Optional[str] = Query(None, min_length=3),
    apellido: Optional[str] = Query(None, min_length=2),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """Lista clientes con filtros (requiere autenticación)"""
    query = db.query(Cliente)

    if ci_nit:
        query = query.filter(Cliente.ci_nit.contains(ci_nit))
    if apellido:
        query = query.filter(Cliente.apellido.ilike(f"%{apellido}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """Obtiene un cliente por ID"""
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_user)
):
    """Actualiza datos de cliente (solo admin)"""
    cliente = db.query(Cliente).get(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)

    db.commit()
    db.refresh(cliente)
    return cliente
