"""
Schemas de Pydantic para validación y serialización de datos
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List


# ============ Schemas de Usuario ============

class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)


class Usuario(UsuarioBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Schemas de Autenticación ============

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============ Schemas de Variable ============

class VariableBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    variable_id_bcra: int
    unidad: Optional[str] = None


class VariableCreate(VariableBase):
    pass


class Variable(VariableBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============ Schemas de Dato BCRA ============

class DatoBCRABase(BaseModel):
    variable_id: int
    fecha: date
    valor: float


class DatoBCRACreate(DatoBCRABase):
    pass


class DatoBCRA(DatoBCRABase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DatoBCRAConVariable(DatoBCRA):
    """Dato con información de la variable incluida"""
    variable: Variable


# ============ Schemas para el Dashboard ============

class UltimoValor(BaseModel):
    """Último valor de una variable para el dashboard"""
    variable: str
    valor: float
    fecha: date
    unidad: Optional[str] = None


class SerieHistorica(BaseModel):
    """Serie histórica de una variable"""
    variable: str
    unidad: Optional[str] = None
    datos: List[dict]  # Lista de {fecha: str, valor: float}


class DashboardData(BaseModel):
    """Datos completos para el dashboard"""
    ultimos_valores: List[UltimoValor]
    series_historicas: dict  # {nombre_variable: SerieHistorica}
    ultima_actualizacion: datetime


# ============ Schemas de respuesta API ============

class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje"""
    message: str
    detail: Optional[str] = None


class StatsResponse(BaseModel):
    """Estadísticas generales del sistema"""
    total_variables: int
    total_datos: int
    ultima_actualizacion: Optional[datetime] = None
    variables_disponibles: List[str]
