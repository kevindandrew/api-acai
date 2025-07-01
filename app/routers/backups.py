import os
import subprocess
import csv
from sqlalchemy import inspect, text
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.personal import Personal
from app.schemas.backup import BackupResponse, BackupListResponse
from app.dependencies import get_current_active_user, require_admin

router = APIRouter(
    prefix="/backups",
    tags=["Backups"],
)

# Configuración
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)


@router.post("/backup-sql", summary="Crear backup SQL simple")
def crear_backup_simple(
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Crea un backup básico en formato SQL (alternativa simple).
    Requiere privilegios de administrador.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_simple_{timestamp}.sql"
        filepath = os.path.join(BACKUP_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # Obtener todas las tablas
            tables = db.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)).fetchall()

            for table in tables:
                table_name = table[0]
                f.write(f"\n-- Tabla: {table_name}\n")

                # 1. Obtener estructura de la tabla (columnas)
                columns = db.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)).fetchall()

                # Construir CREATE TABLE
                f.write(f"CREATE TABLE {table_name} (\n")
                column_defs = []
                for col in columns:
                    col_def = f"  {col[0]} {col[1]}"
                    if col[3]:  # Si tiene longitud máxima (ej. varchar)
                        col_def += f"({col[3]})"
                    if col[2] == 'NO':
                        col_def += " NOT NULL"
                    column_defs.append(col_def)
                f.write(",\n".join(column_defs))

                # 2. Añadir PRIMARY KEY si existe
                pk_columns = db.execute(text(f"""
                    SELECT column_name
                    FROM information_schema.key_column_usage
                    WHERE table_name = '{table_name}'
                    AND constraint_name LIKE '%_pkey'
                    ORDER BY ordinal_position
                """)).fetchall()

                if pk_columns:
                    pk_cols = ", ".join([col[0] for col in pk_columns])
                    f.write(f",\n  PRIMARY KEY ({pk_cols})")

                f.write("\n);\n")

                # 3. Insertar datos
                f.write(f"\n-- Datos para {table_name}\n")
                rows = db.execute(
                    text(f"SELECT * FROM {table_name}")).fetchall()

                if rows:
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append("NULL")
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            elif isinstance(value, datetime):
                                values.append(f"'{value.isoformat()}'")
                            else:
                                escaped_value = str(value).replace("'", "''")
                                values.append(f"'{escaped_value}'")

                        f.write(
                            f"INSERT INTO {table_name} VALUES ({', '.join(values)});\n"
                        )

        return {
            "status": "success",
            "filename": filename,
            "message": f"Backup SQL creado en {filepath}",
            "size_mb": round(os.path.getsize(filepath)/(1024*1024), 2)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear backup: {str(e)}"
        )


@router.get(
    "/listar",
    response_model=List[BackupListResponse],
    summary="Listar todos los backups disponibles"
)
def listar_backups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_active_user)
):
    """
    Lista todos los archivos de backup disponibles con paginación.
    - **skip**: Registros a saltar (para paginación)
    - **limit**: Límite de resultados (max 1000)
    """
    backups = []
    for filename in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if filename.endswith(".sql"):
            filepath = os.path.join(BACKUP_DIR, filename)
            backups.append({
                "filename": filename,
                "size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(
                    os.path.getctime(filepath)
                ).isoformat()
            })

    return backups[skip:skip + limit]


@router.get(
    "/descargar/{filename}",
    summary="Descargar un backup específico"
)
def descargar_backup(
    filename: str,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(get_current_active_user)
):
    """
    Descarga un archivo de backup específico.
    """
    # Validar nombre de archivo por seguridad
    if not filename.endswith(".sql") or "/" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido"
        )

    filepath = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup no encontrado"
        )

    return FileResponse(
        filepath,
        filename=filename,
        media_type="application/sql",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.delete(
    "/eliminar/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un backup"
)
def eliminar_backup(
    filename: str,
    db: Session = Depends(get_db),
    current_user: Personal = Depends(require_admin)
):
    """
    Elimina un archivo de backup específico.
    Requiere privilegios de administrador.
    """
    # Validar nombre de archivo por seguridad
    if not filename.endswith(".sql") or "/" in filename or ".." in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de archivo inválido"
        )

    filepath = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup no encontrado"
        )

    os.remove(filepath)
