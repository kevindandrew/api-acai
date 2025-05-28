from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar todos los routers

from app.routers.auth import router as auth_router
from app.routers.personal import router as personal_router
from app.routers.sucursal import router as sucursal_router
from app.routers.cliente import router as cliente_router
from app.routers.productos import router as productos_router
from app.routers.inventario import router as inventario_router
from app.routers.pedidos import router as pedidos_router
from app.routers.reportes import router as reportes_router
from app.routers.predicciones import router as predicciones_router
app = FastAPI(
    title="API Heladería",
    description="Sistema de gestión para heladerías",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Incluir todos los routers
app.include_router(auth_router)
app.include_router(personal_router)
app.include_router(sucursal_router)
app.include_router(cliente_router)
app.include_router(productos_router)
app.include_router(inventario_router)
app.include_router(pedidos_router)
app.include_router(reportes_router)
app.include_router(predicciones_router)
# Endpoint básico de healthcheck


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}
