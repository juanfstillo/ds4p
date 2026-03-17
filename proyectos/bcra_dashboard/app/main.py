"""
Aplicación principal de FastAPI - BCRA Dashboard
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import timedelta, date, datetime
from typing import List, Optional
import os

from app.database import get_db
from app.models import Usuario, Variable, DatoBCRA
from app import schemas
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Crear aplicación FastAPI
app = FastAPI(
    title="BCRA Dashboard API",
    description="API para visualización de datos del Banco Central de la República Argentina",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta static para el frontend
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ============ ENDPOINTS DE AUTENTICACIÓN ============

@app.post("/api/auth/register", response_model=schemas.Usuario, tags=["Autenticación"])
def register(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario
    """
    # Verificar si el email ya existe
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(usuario.password)
    db_user = Usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.post("/api/auth/login", response_model=schemas.Token, tags=["Autenticación"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login de usuario - devuelve JWT token
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=schemas.Usuario, tags=["Autenticación"])
async def read_users_me(current_user: Usuario = Depends(get_current_active_user)):
    """
    Obtener información del usuario actual
    """
    return current_user


# ============ ENDPOINTS DE VARIABLES ============

@app.get("/api/variables", response_model=List[schemas.Variable], tags=["Variables"])
def listar_variables(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Listar todas las variables disponibles
    """
    variables = db.query(Variable).offset(skip).limit(limit).all()
    return variables


@app.get("/api/variables/{variable_id}", response_model=schemas.Variable, tags=["Variables"])
def obtener_variable(variable_id: int, db: Session = Depends(get_db)):
    """
    Obtener una variable específica por ID
    """
    variable = db.query(Variable).filter(Variable.id == variable_id).first()
    
    if not variable:
        raise HTTPException(status_code=404, detail="Variable no encontrada")
    
    return variable


# ============ ENDPOINTS DE DATOS ============

@app.get("/api/datos/variable/{variable_nombre}", tags=["Datos"])
def obtener_datos_variable(
    variable_nombre: str,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtener datos históricos de una variable específica
    
    Parámetros:
    - variable_nombre: Nombre de la variable (ej: "tipo_cambio_oficial")
    - fecha_desde: Fecha inicial (formato YYYY-MM-DD)
    - fecha_hasta: Fecha final (formato YYYY-MM-DD)
    - limit: Cantidad máxima de registros
    """
    # Buscar la variable
    variable = db.query(Variable).filter(Variable.nombre == variable_nombre).first()
    
    if not variable:
        raise HTTPException(status_code=404, detail="Variable no encontrada")
    
    # Query base
    query = db.query(DatoBCRA).filter(DatoBCRA.variable_id == variable.id)
    
    # Filtrar por fechas si se especifican
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        query = query.filter(DatoBCRA.fecha >= fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
        query = query.filter(DatoBCRA.fecha <= fecha_hasta_dt)
    
    # Ordenar por fecha descendente y limitar
    datos = query.order_by(DatoBCRA.fecha.desc()).limit(limit).all()
    
    return {
        "variable": variable.nombre,
        "descripcion": variable.descripcion,
        "unidad": variable.unidad,
        "total_registros": len(datos),
        "datos": [
            {
                "fecha": dato.fecha.isoformat(),
                "valor": dato.valor
            }
            for dato in reversed(datos)  # Invertir para orden cronológico
        ]
    }


@app.get("/api/datos/ultimos-valores", tags=["Datos"])
def obtener_ultimos_valores(db: Session = Depends(get_db)):
    """
    Obtener el último valor disponible de cada variable
    """
    variables = db.query(Variable).all()
    ultimos_valores = []
    
    for variable in variables:
        ultimo_dato = db.query(DatoBCRA)\
            .filter(DatoBCRA.variable_id == variable.id)\
            .order_by(DatoBCRA.fecha.desc())\
            .first()
        
        if ultimo_dato:
            ultimos_valores.append({
                "variable": variable.nombre,
                "descripcion": variable.descripcion,
                "valor": ultimo_dato.valor,
                "fecha": ultimo_dato.fecha.isoformat(),
                "unidad": variable.unidad
            })
    
    return ultimos_valores


@app.get("/api/dashboard", tags=["Dashboard"])
def obtener_datos_dashboard(
    dias: int = 30,
    db: Session = Depends(get_db)
):
    """
    Obtener todos los datos necesarios para el dashboard
    
    Parámetros:
    - dias: Cantidad de días hacia atrás para las series históricas
    """
    # Calcular fecha desde
    fecha_desde = (datetime.now() - timedelta(days=dias)).date()
    
    # Obtener todas las variables
    variables = db.query(Variable).all()
    
    ultimos_valores = []
    series_historicas = {}
    
    for variable in variables:
        # Último valor
        ultimo_dato = db.query(DatoBCRA)\
            .filter(DatoBCRA.variable_id == variable.id)\
            .order_by(DatoBCRA.fecha.desc())\
            .first()
        
        if ultimo_dato:
            ultimos_valores.append({
                "variable": variable.nombre,
                "descripcion": variable.descripcion,
                "valor": ultimo_dato.valor,
                "fecha": ultimo_dato.fecha.isoformat(),
                "unidad": variable.unidad
            })
        
        # Serie histórica
        datos_historicos = db.query(DatoBCRA)\
            .filter(
                DatoBCRA.variable_id == variable.id,
                DatoBCRA.fecha >= fecha_desde
            )\
            .order_by(DatoBCRA.fecha.asc())\
            .all()
        
        if datos_historicos:
            series_historicas[variable.nombre] = {
                "descripcion": variable.descripcion,
                "unidad": variable.unidad,
                "datos": [
                    {
                        "fecha": dato.fecha.isoformat(),
                        "valor": dato.valor
                    }
                    for dato in datos_historicos
                ]
            }
    
    return {
        "ultimos_valores": ultimos_valores,
        "series_historicas": series_historicas,
        "ultima_actualizacion": datetime.now().isoformat()
    }


# ============ ENDPOINTS DE ESTADÍSTICAS ============

@app.get("/api/stats", response_model=schemas.StatsResponse, tags=["Estadísticas"])
def obtener_estadisticas(db: Session = Depends(get_db)):
    """
    Obtener estadísticas generales del sistema
    """
    total_variables = db.query(Variable).count()
    total_datos = db.query(DatoBCRA).count()
    
    # Última actualización (dato más reciente)
    ultimo_dato = db.query(DatoBCRA).order_by(DatoBCRA.created_at.desc()).first()
    ultima_actualizacion = ultimo_dato.created_at if ultimo_dato else None
    
    # Lista de variables disponibles
    variables = db.query(Variable).all()
    variables_disponibles = [var.nombre for var in variables]
    
    return {
        "total_variables": total_variables,
        "total_datos": total_datos,
        "ultima_actualizacion": ultima_actualizacion,
        "variables_disponibles": variables_disponibles
    }


# ============ ENDPOINT RAÍZ ============

@app.get("/", tags=["General"])
async def root():
    """
    Endpoint raíz - redirige al dashboard
    """
    return {
        "message": "BCRA Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "dashboard": "/dashboard"
    }


@app.get("/health", tags=["General"])
def health_check():
    """
    Health check para monitoreo
    """
    return {"status": "ok"}


# ============ SERVIR FRONTEND ============

@app.get("/dashboard", response_class=HTMLResponse, tags=["Frontend"])
async def dashboard():
    """
    Servir el dashboard HTML
    """
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Dashboard en construcción</h1><p>El archivo index.html no se encuentra.</p>",
            status_code=404
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
